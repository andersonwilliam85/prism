"""InstallationEngine — execute installation, rollback, and preflight checks.

Owns the full installation surface volatility axis. Receives accessors via
constructor injection and handles all steps internally: git config, workspace
creation, repo cloning, tool installation, SSH keys, config file copying,
rollback, sudo sessions, and preflight checks.

Volatility: low-medium — installation surface evolves slowly.
"""

from __future__ import annotations

import json
import secrets
import subprocess
import threading
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

from prism.accessors.command_accessor.i_command_accessor import ICommandAccessor
from prism.accessors.file_accessor.i_file_accessor import IFileAccessor
from prism.accessors.rollback_accessor.i_rollback_accessor import IRollbackAccessor
from prism.accessors.system_accessor.i_system_accessor import ISystemAccessor
from prism.models.installation import (
    InstallationResult,
    InstallContext,
    PrivilegedStep,
    ProgressCallback,
    RollbackAction,
    RollbackState,
    StepResult,
    SudoSession,
)

from . import _resolution, _rollback, _tools, _versions

# ---------------------------------------------------------------------------
# Sudo constants
# ---------------------------------------------------------------------------

_LOCKOUT_SECONDS = 30


class InstallationEngine:
    """Execute installations, rollbacks, and preflight checks.

    All installation steps are handled internally — the manager provides
    context, this engine does everything via injected accessors.
    """

    def __init__(
        self,
        command_accessor: ICommandAccessor,
        file_accessor: IFileAccessor,
        system_accessor: ISystemAccessor,
        rollback_accessor: IRollbackAccessor | None = None,
    ) -> None:
        self._commands = command_accessor
        self._files = file_accessor
        self._system = system_accessor
        self._rollback_accessor = rollback_accessor
        self._progress_callback: ProgressCallback = None
        self._cancel_event: threading.Event | None = None
        self._rollback_state: RollbackState | None = None

    # ==================================================================
    # Public — coarse-grained interface
    # ==================================================================

    def install(self, context: InstallContext) -> InstallationResult:
        """Execute the full installation pipeline."""
        result = InstallationResult(success=False, package_name=context.package_name)
        self._rollback_state = RollbackState(package_name=context.package_name)

        try:
            self._check_cancelled()

            # Preflight checks
            step = self._run_preflight(context.config, context.platform_name)
            result.steps.append(step)
            if not step.success:
                result.error = step.message
                return result

            # Apply proxy/registry settings
            self._apply_proxy_settings(context.proxies, context.npm_registry)
            result.steps.append(StepResult(step="prism_config", success=True))

            # Package manager detection
            self._check_cancelled()
            result.steps.append(self._ensure_package_manager(context.platform_name))

            # Workspace directories
            self._check_cancelled()
            self._create_workspace(context.config, context.merged_config, context.workspace_root)
            result.steps.append(StepResult(step="workspace", success=True))

            # Git config
            self._check_cancelled()
            self._configure_git(context.user_info, context.merged_config)
            result.steps.append(StepResult(step="git_config", success=True))

            # SSH keys
            self._check_cancelled()
            self._ensure_ssh_keys(context.user_info)
            result.steps.append(StepResult(step="ssh_keys", success=True))

            # Clone repositories
            self._check_cancelled()
            self._clone_repos(context.merged_config, str(context.workspace_root))
            result.steps.append(StepResult(step="repositories", success=True))

            # Apply config package (copy files, save merged config)
            self._check_cancelled()
            if context.pkg_path:
                self._apply_config_package(
                    context.pkg_path,
                    context.workspace_root,
                    context.user_info,
                    context.merged_config,
                    context.selected_sub_prisms,
                    context.config,
                )
            result.steps.append(StepResult(step="config_package", success=True))

            # Tool installation
            effective = _tools.build_effective_tool_config(context.merged_config, context.config)
            if context.skip_privileged:
                pending = _tools.plan_privileged_installs(
                    effective,
                    context.platform_name,
                    context.tools_selected,
                    context.tools_excluded,
                    self._commands.pkg_is_installed,
                )
                result.pending_privileged = pending
                result.phase = 1
                result.steps.append(StepResult(step="tools", success=True, skipped=True, message="Deferred"))
                if pending:
                    self._log("tools", f"Deferred {len(pending)} tool installs pending approval")
            else:
                self._install_tools(
                    effective,
                    context.platform_name,
                    context.tools_selected,
                    context.tools_excluded,
                )
                result.steps.append(StepResult(step="tools", success=True))
                result.phase = 2

            # Finalize
            self._finalize(
                context.workspace_root,
                context.package_name,
                context.platform_name,
                context.selected_sub_prisms,
                context.user_info,
                context.config,
            )
            result.steps.append(StepResult(step="finalize", success=True))

            result.success = True
            result.finished_at = datetime.now()

        except _InstallCancelled:
            result.error = "Installation cancelled by user"
            result.finished_at = datetime.now()
            self._log("install", "Cancelled — rolling back...", "warning")
            result.rollback_results = self.rollback()

        except Exception as e:
            result.error = str(e)
            result.finished_at = datetime.now()
            if self._rollback_state and self._rollback_state.actions:
                self._log("install", "Error — rolling back changes...", "warning")
                result.rollback_results = self.rollback()

        return result

    def install_privileged(self, steps: list[PrivilegedStep], platform_name: str) -> InstallationResult:
        """Execute deferred privileged install steps (Phase 2)."""
        result = InstallationResult(success=False, package_name="", phase=2)

        try:
            for step in steps:
                if self._commands.pkg_is_installed(step.name):
                    self._log("tools", f"{step.name} already installed", "success")
                    result.steps.append(StepResult(step="tools", success=True, message=f"{step.name} present"))
                    continue

                self._log("tools", f"Installing {step.name}...")
                try:
                    self._commands.pkg_install(step.name, step.platform or platform_name)
                    self._log("tools", f"Installed {step.name}", "success")
                    result.steps.append(StepResult(step="tools", success=True, message=f"Installed {step.name}"))
                except Exception as e:
                    self._log("tools", f"Failed to install {step.name}: {e}", "warning")
                    result.steps.append(StepResult(step="tools", success=False, message=f"Failed: {step.name} - {e}"))

            result.success = True
            result.finished_at = datetime.now()
        except Exception as e:
            result.error = str(e)
            result.finished_at = datetime.now()

        return result

    def rollback(self, state: RollbackState | None = None) -> list[dict]:
        """Execute rollback for the given or current state."""
        state = state or self._rollback_state
        if not state or not self._rollback_accessor:
            return []

        return _rollback.execute_rollback(
            state,
            self._rollback_accessor,
            self._commands,
            self._log,
        )

    def set_cancel_event(self, event: threading.Event) -> None:
        """Set a threading Event that signals cancellation."""
        self._cancel_event = event

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """Set a callback for progress reporting."""
        self._progress_callback = callback

    # ==================================================================
    # Preflight checks — delegates to _versions submodule
    # ==================================================================

    def check_requirements(self, requirements: dict) -> tuple[bool, list[str]]:
        """Check whether the system meets installation requirements."""
        installed: dict[str, str] = {}
        for key in requirements:
            if key == "onboarding_version":
                continue
            tool_names = ["python3", "python"] if key == "python_version" else [key]
            lookup = "python" if key == "python_version" else key
            for tool_name in tool_names:
                version = self._system.get_installed_version(tool_name)
                if version:
                    installed[lookup] = version
                    break

        return _versions.check_version_requirements(requirements, installed)

    # ==================================================================
    # Package source resolution — delegates to _resolution submodule
    # ==================================================================

    def resolve_package_source(self, package_name: str, sources: list[dict] | None = None) -> dict:
        """Resolve where a package comes from (local, npm, or url)."""
        return _resolution.resolve_package_source(package_name, sources)

    # ==================================================================
    # Sudo session management
    # ==================================================================

    def create_sudo_session(self) -> SudoSession:
        """Create a new sudo session with a cryptographically random token."""
        return SudoSession(token=secrets.token_urlsafe(32))

    def validate_sudo_session(self, session: SudoSession) -> bool:
        """Check if a session is still valid (not expired, not locked)."""
        return not session.is_expired and not session.is_locked

    def record_sudo_attempt(self, session: SudoSession, success: bool) -> SudoSession:
        """Record a password attempt. Resets on success, locks after max failures."""
        if success:
            return replace(session, attempts=0, locked_until=None)

        new_attempts = session.attempts + 1
        locked_until = None
        if new_attempts >= session.max_attempts:
            locked_until = datetime.now() + timedelta(seconds=_LOCKOUT_SECONDS)

        return replace(session, attempts=new_attempts, locked_until=locked_until)

    # ==================================================================
    # Private — installation steps
    # ==================================================================

    def _check_cancelled(self) -> None:
        if self._cancel_event and self._cancel_event.is_set():
            raise _InstallCancelled()

    def _record(self, action_type: str, target: str, rollback_command: str = "", original_value: str = "") -> None:
        if self._rollback_state:
            self._rollback_state.record(
                RollbackAction(
                    action_type=action_type,
                    target=target,
                    rollback_command=rollback_command,
                    original_value=original_value,
                )
            )

    def _log(self, step: str, message: str, level: str = "info") -> None:
        prefix = {"info": "i", "success": "+", "error": "!", "warning": "?"}.get(level, "i")
        print(f"[{prefix}] {message}")
        if self._progress_callback:
            self._progress_callback(step, message, level)

    def _run_preflight(self, config: dict, platform_name: str) -> StepResult:
        requirements = config.get("package", {}).get("requires", {})
        if not requirements:
            self._log("preflight", "No requirements specified — skipping")
            return StepResult(step="preflight", success=True, skipped=True)

        ok, failures = self.check_requirements(requirements)
        if not ok:
            msg = f"Preflight failed: {'; '.join(failures)}"
            self._log("preflight", msg, "error")
            return StepResult(step="preflight", success=False, message=msg)

        self._log("preflight", "All requirements satisfied", "success")
        return StepResult(step="preflight", success=True)

    def _apply_proxy_settings(self, proxies: dict[str, str], npm_registry: str) -> None:
        if proxies.get("http"):
            for key in ("HTTP_PROXY", "http_proxy"):
                self._system.set_env(key, proxies["http"])
            https = proxies.get("https", proxies["http"])
            for key in ("HTTPS_PROXY", "https_proxy"):
                self._system.set_env(key, https)
            no_proxy = proxies.get("no_proxy", "localhost,127.0.0.1")
            for key in ("NO_PROXY", "no_proxy"):
                self._system.set_env(key, no_proxy)
            self._log("prism_config", f"Proxy: {proxies['http']}")

        if npm_registry:
            self._system.set_env("PRISM_NPM_REGISTRY", npm_registry)
            self._log("prism_config", f"NPM registry: {npm_registry}")

    def _ensure_package_manager(self, platform_name: str) -> StepResult:
        if platform_name == "mac":
            if self._commands.pkg_is_installed("brew"):
                self._log("package_manager", "Homebrew already installed", "success")
            else:
                self._log("package_manager", "Homebrew not found — manual install required", "warning")
        elif platform_name in ("ubuntu", "linux"):
            self._log("package_manager", "Using apt (built-in)", "success")
        elif platform_name == "windows":
            if self._commands.pkg_is_installed("choco"):
                self._log("package_manager", "Chocolatey already installed", "success")
            else:
                self._log("package_manager", "Chocolatey not found — manual install required", "warning")
        return StepResult(step="package_manager", success=True)

    def _create_workspace(self, config: dict, merged_config: dict, workspace_root: Path) -> None:
        setup_dirs = config.get("setup", {}).get("install", {}).get("directories", [])
        config_dir_names = [d.get("name", d.get("dest", "")) for d in setup_dirs if isinstance(d, dict)]
        config_dir_names = [d for d in config_dir_names if d]

        dirs = self._plan_workspace(merged_config, config_dir_names)
        if not self._files.exists(workspace_root):
            self._files.mkdir(workspace_root)
            self._record("dir_created", str(workspace_root))
        self._log("workspace", f"Base: {workspace_root}")
        for d in dirs:
            path = workspace_root / d
            if not self._files.exists(path):
                self._files.mkdir(path)
                self._record("dir_created", str(path))
            self._log("workspace", f"Ensured: {d}")

    def _configure_git(self, user_info: dict, merged_config: dict) -> None:
        plan = self._plan_git_config(user_info, merged_config)
        if not plan:
            self._log("git_config", "No git config to set", "warning")
            return

        for key, value in plan:
            original = (
                self._commands.git_get_config(key, scope="global") if hasattr(self._commands, "git_get_config") else ""
            )
            self._commands.git_set_config(key, value, scope="global")
            self._record("config_changed", key, original_value=original or "")
        self._log("git_config", f"Set {len(plan)} git config values", "success")

    def _ensure_ssh_keys(self, user_info: dict) -> None:
        if self._commands.ssh_key_exists():
            self._log("ssh_keys", "SSH key already exists", "success")
            return
        email = user_info.get("email", user_info.get("work_email", "user@example.com"))
        key_path = self._commands.ssh_generate_key(key_type="ed25519", comment=email)
        self._record("file_created", str(key_path))
        self._log("ssh_keys", f"Generated SSH key: {key_path}", "success")

    def _install_tools(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None,
        tools_excluded: list[str] | None,
    ) -> None:
        tools = _tools.resolve_tools(merged_config, platform_name, tools_selected, tools_excluded)
        if not tools:
            self._log("tools", "No tools to install")
            return

        for tool in tools:
            self._check_cancelled()
            name = tool["name"]
            if self._commands.pkg_is_installed(name):
                self._log("tools", f"{name} already installed", "success")
                continue

            # Only install if the YAML defines an explicit command for this platform
            platforms = tool.get("platforms", {})
            cmd = platforms.get(platform_name, "") if isinstance(platforms, dict) else ""
            if not cmd:
                self._log("tools", f"{name} — no install command for {platform_name}, skipping", "warning")
                continue

            self._log("tools", f"Installing {name}...")
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
                self._log("tools", f"Installed {name}", "success")
            except Exception:
                self._log("tools", f"Failed to install {name} — skipping", "warning")

    def _clone_repos(self, merged_config: dict, workspace_root: str) -> None:
        plans = self._plan_repo_clones(merged_config, workspace_root)
        if not plans:
            self._log("repositories", "No repositories to clone")
            return

        for plan in plans:
            dest = Path(plan["dest"])
            if self._files.exists(dest):
                self._log("repositories", f"Already exists: {plan['name']}")
                continue
            self._files.mkdir(dest.parent)
            try:
                self._commands.git_clone(plan["url"], dest)
                self._log("repositories", f"Cloned: {plan['name']}", "success")
            except Exception as e:
                self._log("repositories", f"Failed to clone {plan['name']}: {e}", "warning")

    def _apply_config_package(
        self,
        pkg_path: Path,
        workspace_root: Path,
        user_info: dict,
        merged_config: dict,
        selected_sub_prisms: dict[str, str],
        config: dict,
    ) -> None:
        dest = workspace_root / "docs" / "config"
        if self._files.exists(dest):
            self._files.rmtree(dest)
        self._files.copy(pkg_path, dest)
        self._record("dir_created", str(dest))
        self._log("config_package", "Prism files copied", "success")

        setup_install = config.get("setup", {}).get("install", {})
        for file_entry in setup_install.get("files", []):
            src = pkg_path / file_entry.get("source", "")
            file_dest = workspace_root / file_entry.get("dest", "")
            if self._files.exists(src):
                self._files.mkdir(file_dest.parent)
                self._files.copy(src, file_dest)
                self._log("config_package", f"Copied file: {file_entry['dest']}", "success")

        for dir_entry in setup_install.get("directories", []):
            src = pkg_path / dir_entry.get("source", "")
            dir_dest = workspace_root / dir_entry.get("dest", "")
            if self._files.exists(src):
                if self._files.exists(dir_dest):
                    self._files.rmtree(dir_dest)
                self._files.copy(src, dir_dest)
                self._log("config_package", f"Copied directory: {dir_entry['dest']}", "success")

        self._files.write_yaml(dest / "user-info.yaml", user_info)
        self._record("file_created", str(dest / "user-info.yaml"))

        if merged_config:
            self._files.write_yaml(dest / "merged-config.yaml", merged_config)
            self._record("file_created", str(dest / "merged-config.yaml"))

        if selected_sub_prisms:
            self._files.write_yaml(dest / "selected-sub-prisms.yaml", selected_sub_prisms)
            self._record("file_created", str(dest / "selected-sub-prisms.yaml"))

    def _finalize(
        self,
        workspace_root: Path,
        package_name: str,
        platform_name: str,
        selected_sub_prisms: dict[str, str],
        user_info: dict,
        config: dict,
    ) -> None:
        marker = workspace_root / ".prism_installed"
        marker_data = json.dumps(
            {
                "installed_at": datetime.now().isoformat(),
                "platform": platform_name,
                "prism": package_name,
                "selected_sub_prisms": selected_sub_prisms,
                "user": user_info.get("name", user_info.get("full_name", "Unknown")),
            },
            indent=2,
        )
        self._files.write_text(marker, marker_data)
        self._record("file_created", str(marker))
        self._log("finalize", "Installation complete!", "success")

        post_msg = config.get("setup", {}).get("post_install", {}).get("message")
        if not post_msg:
            post_msg = config.get("package", {}).get("post_install", {}).get("message")
        if post_msg:
            try:
                display = {k: v.replace("-", " ").title() for k, v in selected_sub_prisms.items()}
                post_msg = post_msg.format(**display)
            except (KeyError, ValueError):
                pass
            self._log("finalize", post_msg)

    # ==================================================================
    # Private — planning helpers
    # ==================================================================

    def _plan_git_config(self, user_info: dict, merged_config: dict) -> list[tuple[str, str]]:
        plan: list[tuple[str, str]] = []
        name = user_info.get("name", user_info.get("full_name", ""))
        email = user_info.get("email", user_info.get("work_email", ""))

        if not name or not email:
            git_cfg = merged_config.get("git", {}).get("user", {})
            name = name or git_cfg.get("name", "")
            email = email or git_cfg.get("email", "")

        if name:
            plan.append(("user.name", name))
        if email:
            plan.append(("user.email", email))
        plan.append(("init.defaultBranch", "main"))
        plan.append(("pull.rebase", "false"))

        extra_config = merged_config.get("git", {}).get("config", {})
        for key, value in extra_config.items():
            plan.append((key.replace("_", "."), str(value)))

        return plan

    def _plan_workspace(self, merged_config: dict, config_dirs: list[str] | None = None) -> list[str]:
        if config_dirs:
            dirs = list(config_dirs)
        else:
            dirs = ["projects", "experiments", "learning", "archived", "docs", "tooling"]

        # Collect directories from both workspace.directories and environment.directories
        for key in ("workspace", "environment"):
            extra = merged_config.get(key, {}).get("directories", [])
            if isinstance(extra, list):
                for d in extra:
                    if not isinstance(d, str):
                        continue
                    # Strip ~/dev/ or similar prefixes — make relative to workspace_root
                    d = d.replace("~/", "").strip("/")
                    # Remove workspace_root prefix if present (e.g. "dev/projects" -> "projects")
                    ws_root_name = (
                        merged_config.get("environment", {}).get("workspace_root", "").replace("~/", "").strip("/")
                    )
                    if ws_root_name and d.startswith(ws_root_name + "/"):
                        d = d[len(ws_root_name) + 1 :]
                    if d and d not in dirs:
                        dirs.append(d)
        return dirs

    def _plan_repo_clones(self, merged_config: dict, workspace_root: str) -> list[dict]:
        repositories = merged_config.get("repositories", [])
        if not repositories:
            return []

        ws_root = Path(workspace_root)
        clone_plans: list[dict] = []

        for repo in repositories:
            if isinstance(repo, str):
                url = repo
                name = url.rstrip("/").split("/")[-1].replace(".git", "")
                dest = str(ws_root / "projects" / name)
            elif isinstance(repo, dict):
                url = repo.get("url", "")
                name = repo.get("name", "")
                if not name and url:
                    name = url.rstrip("/").split("/")[-1].replace(".git", "")
                custom_path = repo.get("path")
                dest = str(Path(custom_path).expanduser()) if custom_path else str(ws_root / "projects" / name)
            else:
                continue

            if not url:
                continue
            clone_plans.append({"url": url, "name": name, "dest": dest})

        return clone_plans


class _InstallCancelled(Exception):
    """Internal signal that the user cancelled the installation."""

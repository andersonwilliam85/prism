"""InstallationManager — orchestrate the full install pipeline.

Delegates computation to engines, I/O to accessors.
This is the single orchestrator that replaces the monolithic installer_engine.py.

Volatility: low — pipeline structure and step sequence are stable.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

from prism.accessors.command_accessor.i_command_accessor import ICommandAccessor
from prism.accessors.file_accessor.i_file_accessor import IFileAccessor
from prism.accessors.system_accessor.i_system_accessor import ISystemAccessor
from prism.engines.merge_engine.i_merge_engine import IMergeEngine
from prism.engines.setup_engine.i_setup_engine import ISetupEngine
from prism.engines.validation_engine.i_validation_engine import IValidationEngine
from prism.models.installation import InstallationResult, StepResult
from prism.models.prism_config import BrandingConfig, PrismConfig
from prism.utilities.event_bus.i_event_bus import IEventBus

ProgressCallback = Callable[[str, str, str], None] | None


class InstallationManager:
    """Concrete implementation of IInstallationManager."""

    def __init__(
        self,
        merge_engine: IMergeEngine,
        setup_engine: ISetupEngine,
        validation_engine: IValidationEngine,
        command_accessor: ICommandAccessor,
        file_accessor: IFileAccessor,
        system_accessor: ISystemAccessor,
        event_bus: IEventBus,
        prisms_dir: Path,
    ) -> None:
        self._merge = merge_engine
        self._setup = setup_engine
        self._validation = validation_engine
        self._commands = command_accessor
        self._files = file_accessor
        self._system = system_accessor
        self._event_bus = event_bus
        self._prisms_dir = prisms_dir
        self._progress_callback: ProgressCallback = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str] | None = None,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> InstallationResult:
        """Run the full installation pipeline."""
        result = InstallationResult(success=False, package_name=package_name)
        selected_sub_prisms = selected_sub_prisms or {}

        try:
            # Load and validate
            config = self._files.get_package_config(self._prisms_dir, package_name)
            valid, errors, _warnings = self._validation.validate(config)
            if not valid:
                result.error = f"Validation failed: {'; '.join(errors)}"
                return result

            prism_config = self.load_prism_config(package_name)
            merged = self.merge_tiers(config, selected_sub_prisms)

            # Detect platform
            platform_name, platform_detail = self._system.get_platform()
            self.log("platform", f"Detected: {platform_name} ({platform_detail})")
            result.steps.append(
                StepResult(step="platform", success=True, message=f"{platform_name} ({platform_detail})")
            )

            if platform_name == "unknown":
                result.error = "Unsupported platform"
                result.steps.append(StepResult(step="platform", success=False, message="Unsupported platform"))
                return result

            # Preflight checks
            step_result = self._run_preflight(config, platform_name)
            result.steps.append(step_result)
            if not step_result.success:
                result.error = step_result.message
                return result

            # Apply prism config (proxy, registry)
            self._apply_prism_config(prism_config)
            result.steps.append(StepResult(step="prism_config", success=True))

            # Package manager (brew/choco/apt)
            step_result = self._ensure_package_manager(platform_name)
            result.steps.append(step_result)

            # Workspace folders
            workspace_root = Path.home() / "workspace"
            self._create_workspace(merged, workspace_root)
            result.steps.append(StepResult(step="workspace", success=True))

            # Git config
            self._configure_git(user_info, merged)
            result.steps.append(StepResult(step="git_config", success=True))

            # SSH keys
            self._ensure_ssh_keys(user_info)
            result.steps.append(StepResult(step="ssh_keys", success=True))

            # Install tools
            self._install_tools(merged, platform_name, tools_selected, tools_excluded)
            result.steps.append(StepResult(step="tools", success=True))

            # Clone repositories
            self._clone_repos(merged, str(workspace_root))
            result.steps.append(StepResult(step="repositories", success=True))

            # Apply config package (copy files, save merged config)
            pkg_path = self._files.find_package(self._prisms_dir, package_name)
            if pkg_path:
                self._apply_config_package(pkg_path, workspace_root, user_info, merged, selected_sub_prisms, config)
            result.steps.append(StepResult(step="config_package", success=True))

            # Finalize
            self._finalize(workspace_root, package_name, platform_name, selected_sub_prisms, user_info, config)
            result.steps.append(StepResult(step="finalize", success=True))

            result.success = True
            result.finished_at = datetime.now()
            self._event_bus.publish("installation.complete", {"package": package_name, "success": True})

        except Exception as e:
            result.error = str(e)
            result.finished_at = datetime.now()
            self._event_bus.publish("installation.failed", {"package": package_name, "error": str(e)})

        return result

    def check_readiness(self, requirements: dict) -> tuple[bool, list[str]]:
        """Check whether the system meets installation requirements."""
        installed: dict[str, str] = {}
        for key in requirements:
            if key == "onboarding_version":
                continue
            tool = "python" if key == "python_version" else key
            version = self._system.get_installed_version(tool)
            if version:
                installed[tool] = version
        return self._setup.check_requirements(requirements, installed)

    def load_prism_config(self, package_name: str) -> PrismConfig:
        """Load the prism_config section from a package."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        pc = config.get("prism_config", {})
        branding_raw = pc.get("branding", {})
        return PrismConfig(
            theme=pc.get("theme", "ocean"),
            sources=pc.get("sources", []),
            npm_registry=pc.get("npm_registry", ""),
            unpkg_url=pc.get("unpkg_url", ""),
            proxies=pc.get("proxies", {}),
            branding=(
                BrandingConfig(**{k: v for k, v in branding_raw.items() if k in BrandingConfig.__dataclass_fields__})
                if branding_raw
                else BrandingConfig()
            ),
        )

    def merge_tiers(self, config: dict, selected_sub_prisms: dict[str, str]) -> dict:
        """Build merged config from selected sub-prisms."""
        bundled = config.get("bundled_prisms", {})
        if not bundled:
            return {}

        tier_configs: list[dict] = []
        pkg_path = None

        # Find the package path for resolving config file references
        pkg_section = config.get("package", {})
        pkg_name = pkg_section.get("name", "")
        if pkg_name:
            pkg_path = self._files.find_package(self._prisms_dir, pkg_name)

        for tier_name, tier_prisms in bundled.items():
            if not isinstance(tier_prisms, list):
                continue
            for sub_prism in tier_prisms:
                if not isinstance(sub_prism, dict):
                    continue
                sub_id = sub_prism.get("id")
                config_file = sub_prism.get("config")
                is_required = sub_prism.get("required", False)
                should_include = is_required or (selected_sub_prisms.get(tier_name) == sub_id)

                if should_include and config_file and pkg_path:
                    config_path = pkg_path / config_file
                    if self._files.exists(config_path):
                        try:
                            sub_config = self._files.read_yaml(config_path)
                            tier_configs.append(sub_config)
                            self.log("prism", f"Merged sub-prism: {tier_name}/{sub_id}")
                        except Exception as e:
                            self.log("prism", f"Failed to merge {tier_name}/{sub_id}: {e}", "warning")

        return self._merge.merge_tiers({}, tier_configs)

    def set_progress_callback(self, callback: object | None) -> None:
        """Set the progress callback for UI updates."""
        self._progress_callback = callback  # type: ignore[assignment]

    def log(self, step: str, message: str, level: str = "info") -> None:
        """Log a message and invoke the progress callback."""
        prefix = {"info": "i", "success": "+", "error": "!", "warning": "?"}.get(level, "i")
        print(f"[{prefix}] {message}")
        if self._progress_callback:
            self._progress_callback(step, message, level)

    # ------------------------------------------------------------------
    # Private orchestration steps
    # ------------------------------------------------------------------

    def _run_preflight(self, config: dict, platform_name: str) -> StepResult:
        """Run preflight requirement checks."""
        requirements = config.get("package", {}).get("requires", {})
        if not requirements:
            self.log("preflight", "No requirements specified — skipping")
            return StepResult(step="preflight", success=True, skipped=True)

        installed: dict[str, str] = {}
        for key in requirements:
            if key == "onboarding_version":
                continue
            tool = "python" if key == "python_version" else key
            version = self._system.get_installed_version(tool)
            if version:
                installed[tool] = version

        ok, failures = self._setup.check_requirements(requirements, installed)
        if not ok:
            msg = f"Preflight failed: {'; '.join(failures)}"
            self.log("preflight", msg, "error")
            return StepResult(step="preflight", success=False, message=msg)

        self.log("preflight", "All requirements satisfied", "success")
        return StepResult(step="preflight", success=True)

    def _apply_prism_config(self, prism_config: PrismConfig) -> None:
        """Apply proxy and registry settings to environment."""
        if prism_config.proxies.get("http"):
            for key in ("HTTP_PROXY", "http_proxy"):
                self._system.set_env(key, prism_config.proxies["http"])
            https = prism_config.proxies.get("https", prism_config.proxies["http"])
            for key in ("HTTPS_PROXY", "https_proxy"):
                self._system.set_env(key, https)
            no_proxy = prism_config.proxies.get("no_proxy", "localhost,127.0.0.1")
            for key in ("NO_PROXY", "no_proxy"):
                self._system.set_env(key, no_proxy)
            self.log("prism_config", f"Proxy: {prism_config.proxies['http']}")

        if prism_config.npm_registry:
            self._system.set_env("PRISM_NPM_REGISTRY", prism_config.npm_registry)
            self.log("prism_config", f"NPM registry: {prism_config.npm_registry}")

    def _ensure_package_manager(self, platform_name: str) -> StepResult:
        """Ensure OS package manager is available."""
        if platform_name == "mac":
            if self._commands.pkg_is_installed("brew"):
                self.log("package_manager", "Homebrew already installed", "success")
            else:
                self.log("package_manager", "Homebrew not found — manual install required", "warning")
        elif platform_name in ("ubuntu", "linux"):
            self.log("package_manager", "Using apt (built-in)", "success")
        elif platform_name == "windows":
            if self._commands.pkg_is_installed("choco"):
                self.log("package_manager", "Chocolatey already installed", "success")
            else:
                self.log("package_manager", "Chocolatey not found — manual install required", "warning")
        return StepResult(step="package_manager", success=True)

    def _create_workspace(self, merged_config: dict, workspace_root: Path) -> None:
        """Create workspace directory structure."""
        dirs = self._setup.plan_workspace(merged_config)
        for d in dirs:
            path = workspace_root / d
            self._files.mkdir(path)
            self.log("workspace", f"Ensured: {d}")

    def _configure_git(self, user_info: dict, merged_config: dict) -> None:
        """Configure git global settings."""
        plan = self._setup.plan_git_config(user_info, merged_config)
        if not plan:
            self.log("git_config", "No git config to set", "warning")
            return

        for key, value in plan:
            self._commands.git_set_config(key, value, scope="global")
        self.log("git_config", f"Set {len(plan)} git config values", "success")

    def _ensure_ssh_keys(self, user_info: dict) -> None:
        """Generate SSH keys if they don't exist."""
        if self._commands.ssh_key_exists():
            self.log("ssh_keys", "SSH key already exists", "success")
            return
        email = user_info.get("email", user_info.get("work_email", "user@example.com"))
        key_path = self._commands.ssh_generate_key(key_type="ed25519", comment=email)
        self.log("ssh_keys", f"Generated SSH key: {key_path}", "success")

    def _install_tools(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None,
        tools_excluded: list[str] | None,
    ) -> None:
        """Resolve and install tools."""
        tools = self._setup.resolve_tools(merged_config, platform_name, tools_selected, tools_excluded)
        if not tools:
            self.log("tools", "No tools to install")
            return

        for tool in tools:
            name = tool["name"]
            if self._commands.pkg_is_installed(name):
                self.log("tools", f"{name} already installed", "success")
            else:
                self.log("tools", f"Installing {name}...")
                try:
                    self._commands.pkg_install(name, platform_name)
                    self.log("tools", f"Installed {name}", "success")
                except Exception:
                    self.log("tools", f"Failed to install {name} — skipping", "warning")

    def _clone_repos(self, merged_config: dict, workspace_root: str) -> None:
        """Clone repositories from merged config."""
        plans = self._setup.plan_repo_clones(merged_config, workspace_root)
        if not plans:
            self.log("repositories", "No repositories to clone")
            return

        for plan in plans:
            dest = Path(plan["dest"])
            if self._files.exists(dest):
                self.log("repositories", f"Already exists: {plan['name']}")
                continue
            self._files.mkdir(dest.parent)
            try:
                self._commands.git_clone(plan["url"], dest)
                self.log("repositories", f"Cloned: {plan['name']}", "success")
            except Exception as e:
                self.log("repositories", f"Failed to clone {plan['name']}: {e}", "warning")

    def _apply_config_package(
        self,
        pkg_path: Path,
        workspace_root: Path,
        user_info: dict,
        merged_config: dict,
        selected_sub_prisms: dict[str, str],
        config: dict,
    ) -> None:
        """Copy prism files and save merged config."""
        dest = workspace_root / "docs" / "config"

        # Remove old config if present, then copy
        if self._files.exists(dest):
            self._files.rmtree(dest)
        self._files.copy(pkg_path, dest)
        self.log("config_package", "Prism files copied", "success")

        # Process setup.install directives
        setup_install = config.get("setup", {}).get("install", {})
        for file_entry in setup_install.get("files", []):
            src = pkg_path / file_entry.get("source", "")
            file_dest = workspace_root / file_entry.get("dest", "")
            if self._files.exists(src):
                self._files.mkdir(file_dest.parent)
                self._files.copy(src, file_dest)
                self.log("config_package", f"Copied file: {file_entry['dest']}", "success")

        for dir_entry in setup_install.get("directories", []):
            src = pkg_path / dir_entry.get("source", "")
            dir_dest = workspace_root / dir_entry.get("dest", "")
            if self._files.exists(src):
                if self._files.exists(dir_dest):
                    self._files.rmtree(dir_dest)
                self._files.copy(src, dir_dest)
                self.log("config_package", f"Copied directory: {dir_entry['dest']}", "success")

        # Save user info
        self._files.write_yaml(dest / "user-info.yaml", user_info)

        # Save merged config
        if merged_config:
            self._files.write_yaml(dest / "merged-config.yaml", merged_config)

        # Save selection record
        if selected_sub_prisms:
            self._files.write_yaml(dest / "selected-sub-prisms.yaml", selected_sub_prisms)

    def _finalize(
        self,
        workspace_root: Path,
        package_name: str,
        platform_name: str,
        selected_sub_prisms: dict[str, str],
        user_info: dict,
        config: dict,
    ) -> None:
        """Write installation marker and show post-install message."""
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
        self.log("finalize", "Installation complete!", "success")

        post_msg = config.get("setup", {}).get("post_install", {}).get("message")
        if not post_msg:
            post_msg = config.get("package", {}).get("post_install", {}).get("message")
        if post_msg:
            self.log("finalize", post_msg)

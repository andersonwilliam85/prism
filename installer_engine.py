#!/usr/bin/env python3
"""
Prism Installation Engine

Core installation logic used by both CLI and Web UI installers.
Handles platform detection, tool installation, configuration merging,
repository cloning, and progress tracking.

A "prism" package contains:
  - prism_config:    Configures Prism itself (theme, proxy, registry, branding)
  - bundled_prisms:  Hierarchical sub-configs (base + optional tiers like roles, divisions, teams)
  - user_info_fields: What info to collect from the user

Installation flow:
  1. Load package.yaml from chosen prism
  2. Apply prism_config (proxy, registry, theme)
  3. Merge selected sub-prisms using ConfigMerger
  4. Use merged config to drive tool install, git setup, repo cloning
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], check=False)
    import yaml


class InstallationEngine:
    """Core installation engine for Prism setup"""

    def __init__(
        self,
        config_package=None,
        user_info=None,
        selected_sub_prisms=None,
        tools_selected=None,
        tools_excluded=None,
        progress_callback=None,
    ):
        """
        Initialize installation engine.

        Args:
            config_package:      Path to prism directory (e.g. "prisms/startup.prism")
            user_info:           Dict of user-supplied info (name, email, etc.)
            selected_sub_prisms: Dict mapping tier name → sub-prism id the user chose.
                                 e.g. {"roles": "full-stack", "stacks": "mern"}
                                 Required sub-prisms (base tier) are always included automatically.
            tools_selected:      Optional list of tool names to install (whitelist). If set, only these tools are installed.
            tools_excluded:      Optional list of tool names to skip (blacklist). Applied after tools_selected.
            progress_callback:   Optional callable(step, message, level) for UI progress updates.
        """
        self.root_dir = Path(__file__).parent
        self.config_package = config_package
        self.user_info = user_info or {}
        self.selected_sub_prisms = selected_sub_prisms or {}
        self.tools_selected = tools_selected or []
        self.tools_excluded = tools_excluded or []
        self.progress_callback = progress_callback
        self.platform_name, self.platform_detail = self._detect_platform()
        self.home = Path.home()
        self.workspace = self.home / "workspace"

        # These are populated by _load_prism_config()
        self.prism_meta = {}  # prism_config section: theme, proxy, registry, branding
        self.merged_config = {}  # deep-merged result of all selected sub-prisms

        if config_package:
            self._load_prism_config()

    # =========================================================================
    # Prism config loading and sub-prism merging
    # =========================================================================

    def _load_prism_config(self):
        """
        Load the prism's package.yaml and build a merged configuration from
        the selected sub-prisms declared in bundled_prisms.

        Required sub-prisms (required: true) are always included.
        Optional tiers use self.selected_sub_prisms to determine which to include.
        """
        package_path = Path(self.config_package)
        package_yaml = package_path / "package.yaml"

        if not package_yaml.exists():
            return

        try:
            with open(package_yaml) as f:
                pkg_data = yaml.safe_load(f) or {}
        except Exception as e:
            self.log("prism", f"Could not read package.yaml: {e}", "warning")
            return

        # Extract prism meta-configuration (theme, proxy, registry, branding)
        self.prism_meta = pkg_data.get("prism_config", {})

        # Build merged config from bundled sub-prisms
        bundled = pkg_data.get("bundled_prisms", {})
        if not bundled:
            return  # Old-style package — no sub-prism merging

        # Import ConfigMerger from scripts/
        scripts_dir = self.root_dir / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        try:
            from config_merger import ConfigMerger

            merger = ConfigMerger.__new__(ConfigMerger)
            merger.rules = merger._default_rules()
        except Exception as e:
            self.log("prism", f"ConfigMerger unavailable: {e}", "warning")
            return

        merged = {}

        # Walk each tier in bundled_prisms in definition order
        for tier_name, tier_prisms in bundled.items():
            if not isinstance(tier_prisms, list):
                continue

            for sub_prism in tier_prisms:
                if not isinstance(sub_prism, dict):
                    continue

                sub_id = sub_prism.get("id")
                config_file = sub_prism.get("config")
                is_required = sub_prism.get("required", False)

                # Include if required, OR if the user selected this id for this tier
                should_include = is_required or (self.selected_sub_prisms.get(tier_name) == sub_id)

                if should_include and config_file:
                    config_path = package_path / config_file
                    if config_path.exists():
                        try:
                            with open(config_path) as f:
                                sub_config = yaml.safe_load(f) or {}
                            merged = merger._merge_level(merged, sub_config, tier_name)
                            self.log("prism", f"Merged sub-prism: {tier_name}/{sub_id}", "info")
                        except Exception as e:
                            self.log("prism", f"Failed to merge {tier_name}/{sub_id}: {e}", "warning")

        self.merged_config = merged

    def _apply_proxy_settings(self):
        """
        Apply proxy settings to the environment.
        Reads from prism_config.proxies first, falls back to merged config's
        environment.proxy section.
        """
        proxies = self.prism_meta.get("proxies", {})

        if not proxies:
            env_config = self.merged_config.get("environment", {})
            proxy_config = env_config.get("proxy", {})
            if proxy_config.get("enabled", True) and proxy_config.get("http"):
                proxies = {
                    "http": proxy_config.get("http"),
                    "https": proxy_config.get("https", proxy_config.get("http")),
                    "no_proxy": proxy_config.get("no_proxy", "localhost,127.0.0.1"),
                }

        if proxies.get("http"):
            self.log("prism", f"Applying proxy: {proxies['http']}", "info")
            os.environ["HTTP_PROXY"] = proxies["http"]
            os.environ["http_proxy"] = proxies["http"]
            os.environ["HTTPS_PROXY"] = proxies.get("https", proxies["http"])
            os.environ["https_proxy"] = proxies.get("https", proxies["http"])
            os.environ["NO_PROXY"] = proxies.get("no_proxy", "localhost,127.0.0.1")
            os.environ["no_proxy"] = proxies.get("no_proxy", "localhost,127.0.0.1")

        npm_registry = self.prism_meta.get("npm_registry", "") or os.environ.get("PRISM_NPM_REGISTRY", "")
        if npm_registry:
            os.environ["PRISM_NPM_REGISTRY"] = npm_registry
            self.log("prism", f"Using npm registry: {npm_registry}", "info")

    # =========================================================================
    # Logging and platform helpers
    # =========================================================================

    def log(self, step, message, level="info"):
        """Log a message and invoke the progress callback."""
        prefix = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(level, "ℹ️")
        print(f"{prefix} {message}")
        if self.progress_callback:
            self.progress_callback(step, message, level)

    def _detect_platform(self):
        """Detect operating system and return (platform_name, platform_detail)."""
        system = platform.system().lower()
        if system == "darwin":
            machine = platform.machine()
            return "mac", "Apple Silicon" if machine == "arm64" else "Intel"
        elif system == "windows":
            return "windows", platform.version()
        elif system == "linux":
            try:
                with open("/etc/os-release") as f:
                    if "ubuntu" in f.read().lower():
                        return "ubuntu", platform.version()
            except Exception:
                pass
            return "linux", platform.version()
        return "unknown", ""

    def run_command(self, cmd, check=True, shell=False, capture_output=False):
        """Run a shell command safely."""
        try:
            if isinstance(cmd, str) and not shell:
                cmd = cmd.split()
            result = subprocess.run(cmd, check=check, shell=shell, capture_output=capture_output, text=True)
            return result
        except subprocess.CalledProcessError as e:
            self.log("command", f"Command failed: {e}", "error")
            if check:
                raise
            return None

    # =========================================================================
    # Installation orchestration
    # =========================================================================

    def install(self):
        """Run the full installation process."""
        steps = [
            ("platform", self.step_detect_platform),
            ("preflight", self.step_preflight_check),
            ("prism_config", self.step_apply_prism_config),
            ("package_manager", self.step_install_package_manager),
            ("folder_structure", self.step_create_folder_structure),
            ("git", self.step_install_git),
            ("git_config", self.step_configure_git),
            ("ssh_keys", self.step_generate_ssh_keys),
            ("tools", self.step_install_tools),
            ("repositories", self.step_clone_repositories),
            ("config_package", self.step_apply_config_package),
            ("finalize", self.step_finalize),
        ]

        for step_name, step_func in steps:
            try:
                self.log(step_name, f"Starting: {step_name.replace('_', ' ').title()}")
                step_func()
                self.log(step_name, f"Completed: {step_name.replace('_', ' ').title()}", "success")
            except Exception as e:
                self.log(step_name, f"Failed: {str(e)}", "error")
                raise

        return True

    # =========================================================================
    # Installation steps
    # =========================================================================

    def step_detect_platform(self):
        """Step 1: Detect and validate platform."""
        self.log("platform", f"Detected: {self.platform_name} ({self.platform_detail})")
        if self.platform_name == "unknown":
            raise Exception("Unsupported platform")

    def step_preflight_check(self):
        """Step 2: Validate package.requires before proceeding with installation."""
        if not self.config_package:
            return

        package_yaml = Path(self.config_package) / "package.yaml"
        if not package_yaml.exists():
            return

        try:
            with open(package_yaml) as f:
                pkg_data = yaml.safe_load(f) or {}
        except Exception:
            return

        requires = pkg_data.get("package", {}).get("requires", {})
        if not requires:
            self.log("preflight", "No requirements specified — skipping preflight", "info")
            return

        failures = []

        # Check python_version
        python_req = requires.get("python_version")
        if python_req:
            current = f"{sys.version_info.major}.{sys.version_info.minor}"
            if not self._version_satisfies(current, python_req):
                failures.append(f"Python {python_req} required, found {current}")
            else:
                self.log("preflight", f"Python {current} satisfies {python_req}", "success")

        # Check git
        git_req = requires.get("git")
        if git_req:
            git_path = shutil.which("git")
            if not git_path:
                failures.append("git is required but not found")
            else:
                self.log("preflight", "git found", "success")

        # Check arbitrary commands (e.g. node, docker)
        for key, value in requires.items():
            if key in ("python_version", "git", "onboarding_version"):
                continue
            # Treat as a command that must be available
            if shutil.which(key):
                self.log("preflight", f"{key} found", "success")
            else:
                failures.append(f"{key} is required but not found")

        if failures:
            for f in failures:
                self.log("preflight", f, "error")
            raise Exception(f"Preflight check failed: {'; '.join(failures)}")

        self.log("preflight", "All requirements satisfied", "success")

    def _version_satisfies(self, current, requirement):
        """Check if current version satisfies a requirement like '>=3.8'."""
        req = requirement.strip()
        if req.startswith(">="):
            return self._compare_versions(current, req[2:]) >= 0
        elif req.startswith(">"):
            return self._compare_versions(current, req[1:]) > 0
        elif req.startswith("<="):
            return self._compare_versions(current, req[2:]) <= 0
        elif req.startswith("<"):
            return self._compare_versions(current, req[1:]) < 0
        elif req.startswith("=="):
            return self._compare_versions(current, req[2:]) == 0
        return True  # Unknown format — don't block

    def _compare_versions(self, a, b):
        """Compare two version strings. Returns -1, 0, or 1."""
        a_parts = [int(x) for x in a.strip().split(".")]
        b_parts = [int(x) for x in b.strip().split(".")]
        for i in range(max(len(a_parts), len(b_parts))):
            av = a_parts[i] if i < len(a_parts) else 0
            bv = b_parts[i] if i < len(b_parts) else 0
            if av < bv:
                return -1
            if av > bv:
                return 1
        return 0

    def step_apply_prism_config(self):
        """Step 3: Apply prism meta-configuration (proxy, registry, theme)."""
        if not self.prism_meta:
            self.log("prism_config", "No prism_config found — using defaults", "info")
            return

        theme = self.prism_meta.get("theme", "ocean")
        self.log("prism_config", f"Theme: {theme}", "info")

        branding = self.prism_meta.get("branding", {})
        if branding.get("name"):
            self.log("prism_config", f"Branding: {branding['name']}", "info")

        self._apply_proxy_settings()

    def step_install_package_manager(self):
        """Step 3: Install OS package manager if needed."""
        if self.platform_name == "mac":
            if shutil.which("brew"):
                self.log("package_manager", "Homebrew already installed", "success")
                return
            self.log("package_manager", "Installing Homebrew...")
            install_cmd = (
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            self.run_command(install_cmd, shell=True)

        elif self.platform_name == "windows":
            if shutil.which("choco"):
                self.log("package_manager", "Chocolatey already installed", "success")
                return
            self.log("package_manager", "Installing Chocolatey...")
            install_cmd = (
                'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; '
                "[System.Net.ServicePointManager]::SecurityProtocol = "
                "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))\""
            )
            self.run_command(install_cmd, shell=True)

        elif self.platform_name in ("ubuntu", "linux"):
            self.log("package_manager", "Using apt (built-in)", "success")
            self.run_command("sudo apt-get update", shell=True, check=False)

    def step_create_folder_structure(self):
        """Step 4: Create workspace folder structure."""
        folders = [
            self.workspace,
            self.workspace / "projects",
            self.workspace / "experiments",
            self.workspace / "learning",
            self.workspace / "archived",
            self.workspace / "docs",
            self.workspace / "tooling",
        ]
        for folder in folders:
            if not folder.exists():
                folder.mkdir(parents=True)
                self.log("folder_structure", f"Created: {folder.relative_to(self.home)}")
            else:
                self.log("folder_structure", f"Exists: {folder.relative_to(self.home)}")

    def step_install_git(self):
        """Step 5: Install Git."""
        if shutil.which("git"):
            version = self.run_command("git --version", capture_output=True).stdout.strip()
            self.log("git", f"Git already installed: {version}", "success")
            return
        self.log("git", "Installing Git...")
        if self.platform_name == "mac":
            self.run_command("brew install git")
        elif self.platform_name == "windows":
            self.run_command("choco install git -y", shell=True)
        elif self.platform_name in ("ubuntu", "linux"):
            self.run_command("sudo apt-get install -y git", shell=True)

    def step_configure_git(self):
        """Step 6: Configure global Git settings from user info."""
        name = self.user_info.get("name", self.user_info.get("full_name", ""))
        email = self.user_info.get("email", self.user_info.get("work_email", ""))

        # Fall back to merged config git settings if user info incomplete
        if not name or not email:
            git_cfg = self.merged_config.get("git", {}).get("user", {})
            name = name or git_cfg.get("name", "")
            email = email or git_cfg.get("email", "")

        if not name or not email:
            self.log("git_config", "Skipping git config — no user info provided", "warning")
            return

        self.log("git_config", f"Configuring Git for {name} <{email}>")
        self.run_command(f'git config --global user.name "{name}"', shell=True)
        self.run_command(f'git config --global user.email "{email}"', shell=True)
        self.run_command("git config --global init.defaultBranch main", shell=True)
        self.run_command("git config --global pull.rebase false", shell=True)

    def step_generate_ssh_keys(self):
        """Step 7: Generate SSH keys if they don't exist."""
        ssh_dir = self.home / ".ssh"
        ssh_key = ssh_dir / "id_ed25519"

        if ssh_key.exists():
            self.log("ssh_keys", "SSH key already exists", "success")
            return

        ssh_dir.mkdir(exist_ok=True, mode=0o700)
        email = self.user_info.get("email", self.user_info.get("work_email", "user@example.com"))
        self.log("ssh_keys", f"Generating SSH key for {email}")
        self.run_command(f'ssh-keygen -t ed25519 -C "{email}" -f {ssh_key} -N ""', shell=True)
        self.log("ssh_keys", f"SSH key generated: {ssh_key}", "success")
        self.log("ssh_keys", f"Public key: {ssh_key}.pub", "info")

    def step_install_tools(self):
        """Step 8: Install tools declared in the merged prism configuration."""
        tools = self._get_tools_from_merged_config()
        if not tools:
            self.log("tools", "No tools declared in prism configuration", "info")
            return
        for tool in tools:
            self._install_tool(tool)

    def _get_tools_from_merged_config(self):
        """
        Get the tools list from the merged sub-prism configuration.
        Falls back to the old package.tools format for backward compatibility.
        Applies tools_selected (whitelist) and tools_excluded (blacklist) filters.
        """
        # New format: tools_required in merged sub-configs
        tools = self.merged_config.get("tools_required", [])

        if not tools:
            # Old format: package.tools in package.yaml
            if not self.config_package:
                return []
            package_yaml = Path(self.config_package) / "package.yaml"
            if not package_yaml.exists():
                return []
            try:
                with open(package_yaml) as f:
                    pkg_config = yaml.safe_load(f) or {}
                tools = pkg_config.get("package", {}).get("tools", []) or pkg_config.get("tools", [])
            except Exception:
                return []

        if not tools:
            return []

        def tool_name(t):
            return t if isinstance(t, str) else t.get("name", "")

        # Whitelist: if tools_selected is set, only include those
        if self.tools_selected:
            selected = set(self.tools_selected)
            tools = [t for t in tools if tool_name(t) in selected]

        # Blacklist: always exclude these
        if self.tools_excluded:
            excluded = set(self.tools_excluded)
            tools = [t for t in tools if tool_name(t) not in excluded]

        return tools

    def _install_tool(self, tool):
        """Install a single tool by name."""
        tool_name = tool if isinstance(tool, str) else tool.get("name", "")
        if not tool_name:
            return

        if shutil.which(tool_name):
            self.log("tools", f"{tool_name} already installed", "success")
            return

        self.log("tools", f"Installing {tool_name}...")
        try:
            if self.platform_name == "mac":
                self.run_command(f"brew install {tool_name}")
            elif self.platform_name == "windows":
                self.run_command(f"choco install {tool_name} -y", shell=True)
            elif self.platform_name in ("ubuntu", "linux"):
                self.run_command(f"sudo apt-get install -y {tool_name}", shell=True)
        except Exception:
            self.log("tools", f"Failed to install {tool_name} — skipping", "warning")

    def step_clone_repositories(self):
        """Step 9: Clone repositories declared in the merged prism configuration."""
        repositories = self.merged_config.get("repositories", [])
        if not repositories:
            self.log("repositories", "No repositories declared in prism configuration", "info")
            return

        for repo in repositories:
            if isinstance(repo, str):
                url = repo
                name = url.rstrip("/").split("/")[-1].replace(".git", "")
                dest = self.workspace / "projects" / name
            else:
                url = repo.get("url", "")
                name = repo.get("name", url.rstrip("/").split("/")[-1].replace(".git", "") if url else "")
                custom_path = repo.get("path")
                dest = Path(custom_path).expanduser() if custom_path else self.workspace / "projects" / name

            if not url:
                continue

            if dest.exists():
                self.log("repositories", f"Already exists: {name}", "info")
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            self.log("repositories", f"Cloning: {name} ...")
            try:
                self.run_command(f'git clone "{url}" "{dest}"', shell=True)
                self.log("repositories", f"Cloned: {name}", "success")
            except Exception as e:
                self.log("repositories", f"Failed to clone {name}: {e}", "warning")

    def step_apply_config_package(self):
        """Step 10: Copy prism files and save the merged configuration."""
        if not self.config_package:
            self.log("config_package", "No prism specified", "warning")
            return

        package_path = Path(self.config_package)
        if not package_path.exists():
            self.log("config_package", f"Prism not found: {package_path}", "error")
            return

        # Copy prism source files to workspace
        dest = self.workspace / "docs" / "config"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(package_path, dest)
        self.log("config_package", f"Prism files copied to {dest.relative_to(self.home)}", "success")

        # Process setup.install directives (files and directories)
        try:
            with open(package_path / "package.yaml") as f:
                pkg_data = yaml.safe_load(f) or {}
            setup_install = pkg_data.get("setup", {}).get("install", {})

            # Copy individual files
            for file_entry in setup_install.get("files", []):
                src = package_path / file_entry.get("source", "")
                file_dest = self.workspace / file_entry.get("dest", "")
                if src.exists() and src.is_file():
                    file_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, file_dest)
                    self.log("config_package", f"Copied file: {file_entry['dest']}", "success")
                else:
                    self.log("config_package", f"Source file not found: {file_entry.get('source')}", "warning")

            # Copy directories
            for dir_entry in setup_install.get("directories", []):
                src = package_path / dir_entry.get("source", "")
                dir_dest = self.workspace / dir_entry.get("dest", "")
                if src.exists() and src.is_dir():
                    if dir_dest.exists():
                        shutil.rmtree(dir_dest)
                    shutil.copytree(src, dir_dest)
                    self.log("config_package", f"Copied directory: {dir_entry['dest']}", "success")
                else:
                    self.log("config_package", f"Source directory not found: {dir_entry.get('source')}", "warning")
        except Exception as e:
            self.log("config_package", f"Error processing setup.install: {e}", "warning")

        # Save user info alongside config
        user_config_file = dest / "user-info.yaml"
        with open(user_config_file, "w") as f:
            yaml.dump(self.user_info, f, default_flow_style=False)
        self.log("config_package", "User info saved", "success")

        # Save the fully merged configuration so downstream tools can use it
        if self.merged_config:
            merged_file = dest / "merged-config.yaml"
            with open(merged_file, "w") as f:
                yaml.dump(self.merged_config, f, default_flow_style=False, sort_keys=False)
            self.log("config_package", "Merged prism configuration saved to merged-config.yaml", "success")

        # Save which sub-prisms were selected for reference
        if self.selected_sub_prisms:
            selection_file = dest / "selected-sub-prisms.yaml"
            with open(selection_file, "w") as f:
                yaml.dump(self.selected_sub_prisms, f, default_flow_style=False)

    def step_finalize(self):
        """Step 11: Write installation marker and show next steps."""
        marker = self.workspace / ".prism_installed"
        marker.write_text(
            json.dumps(
                {
                    "installed_at": datetime.now().isoformat(),
                    "platform": self.platform_name,
                    "prism": str(self.config_package) if self.config_package else None,
                    "selected_sub_prisms": self.selected_sub_prisms,
                    "user": self.user_info.get("name", self.user_info.get("full_name", "Unknown")),
                },
                indent=2,
            )
        )

        self.log("finalize", "Installation complete! 🎉", "success")
        self.log("finalize", f"Workspace: {self.workspace}", "info")

        # Show post-install message from prism if available
        if self.config_package:
            package_yaml = Path(self.config_package) / "package.yaml"
            try:
                with open(package_yaml) as f:
                    pkg_data = yaml.safe_load(f) or {}
                msg = pkg_data.get("setup", {}).get("post_install", {}).get("message") or pkg_data.get(
                    "package", {}
                ).get("post_install", {}).get("message")
                if msg:
                    print(f"\n{msg}")
            except Exception:
                pass

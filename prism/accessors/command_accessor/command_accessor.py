"""CommandAccessor — CLI subprocess execution.

Consolidates GitCommandAccessor + SSHKeyAccessor + PlatformPackageAccessor.
Pure I/O translation: wraps subprocess calls to CLI tools.
No business logic.

Volatility: low — CLI tool interfaces are stable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class CommandAccessor:
    """Concrete implementation of ICommandAccessor."""

    # Platform → install command template
    _INSTALL_COMMANDS: dict[str, list[str]] = {
        "mac": ["brew", "install", "{pkg}"],
        "windows": ["choco", "install", "{pkg}", "-y"],
        "ubuntu": ["sudo", "apt-get", "install", "-y", "{pkg}"],
        "linux": ["sudo", "apt-get", "install", "-y", "{pkg}"],
    }

    def __init__(self, ssh_dir: Path | None = None):
        """Initialize with optional custom SSH directory.

        Args:
            ssh_dir: Path to .ssh directory. Defaults to ~/.ssh.
        """
        self._ssh_dir = ssh_dir or Path.home() / ".ssh"

    # ------------------------------------------------------------------
    # Git commands
    # ------------------------------------------------------------------

    def git_set_config(self, key: str, value: str, scope: str = "global") -> None:
        """Set a git config value."""
        cmd = ["git", "config", f"--{scope}", key, value]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise FileNotFoundError("git is not installed or not on PATH")

    def git_clone(self, url: str, target: Path) -> None:
        """Clone a git repository to the target directory."""
        cmd = ["git", "clone", url, str(target)]
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120, env=env)
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"git clone timed out for {url}")
        except FileNotFoundError:
            raise FileNotFoundError("git is not installed or not on PATH")

    # ------------------------------------------------------------------
    # SSH commands
    # ------------------------------------------------------------------

    def ssh_generate_key(self, key_type: str = "ed25519", comment: str = "") -> Path:
        """Generate an SSH key pair."""
        self._ssh_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        key_path = self._ssh_dir / f"id_{key_type}"

        cmd = ["ssh-keygen", "-t", key_type, "-f", str(key_path), "-N", ""]
        if comment:
            cmd.extend(["-C", comment])

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise FileNotFoundError("ssh-keygen is not installed or not on PATH")

        return key_path

    def ssh_key_exists(self) -> bool:
        """Check whether an SSH key already exists."""
        key_names = ["id_ed25519", "id_rsa", "id_ecdsa"]
        return any((self._ssh_dir / name).exists() for name in key_names)

    # ------------------------------------------------------------------
    # Package manager commands
    # ------------------------------------------------------------------

    def pkg_install(self, package_name: str, platform_name: str) -> bool:
        """Install a package using the platform's package manager."""
        if platform_name not in self._INSTALL_COMMANDS:
            raise ValueError(f"Unsupported platform: {platform_name}")

        cmd_template = self._INSTALL_COMMANDS[platform_name]
        cmd = [part.replace("{pkg}", package_name) for part in cmd_template]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def pkg_is_installed(self, package_name: str) -> bool:
        """Check whether a command/tool is available on PATH."""
        return shutil.which(package_name) is not None

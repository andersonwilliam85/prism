"""PlatformPackageAccessor — brew/choco/apt command execution.

Pure I/O translation: wraps subprocess calls to platform package managers.
No business logic — just command dispatch based on platform name.
"""

from __future__ import annotations

import shutil
import subprocess


class PlatformPackageAccessor:
    """Concrete implementation of IPlatformPackageAccessor."""

    # Maps platform name to install command template
    _INSTALL_COMMANDS: dict[str, list[str]] = {
        "mac": ["brew", "install", "{pkg}"],
        "windows": ["choco", "install", "{pkg}", "-y"],
        "ubuntu": ["sudo", "apt-get", "install", "-y", "{pkg}"],
        "linux": ["sudo", "apt-get", "install", "-y", "{pkg}"],
    }

    def install(self, package_name: str, platform_name: str) -> bool:
        """Install a package using the platform's package manager.

        Args:
            package_name: Name of the package to install (e.g. "git", "node").
            platform_name: Platform identifier ("mac", "windows", "ubuntu", "linux").

        Returns:
            True if installation succeeded, False otherwise.

        Raises:
            ValueError: If the platform is not supported.
        """
        if platform_name not in self._INSTALL_COMMANDS:
            raise ValueError(f"Unsupported platform: {platform_name}")

        cmd_template = self._INSTALL_COMMANDS[platform_name]
        cmd = [part.replace("{pkg}", package_name) for part in cmd_template]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def is_installed(self, package_name: str) -> bool:
        """Check whether a command/tool is available on PATH.

        Args:
            package_name: Name of the tool to check (e.g. "git", "node").

        Returns:
            True if the tool is found on PATH.
        """
        return shutil.which(package_name) is not None

"""SystemAccessor — platform detection, OS info, and environment variables.

Pure I/O translation: wraps platform module, /etc/os-release parsing,
subprocess version checks, and os.environ access.

Volatility: low — OS detection and env var APIs are stable.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess


class SystemAccessor:
    """Concrete implementation of ISystemAccessor."""

    def get_platform(self) -> tuple[str, str]:
        """Detect the current operating system.

        Returns:
            A tuple of (platform_name, platform_detail) where platform_name
            is one of "mac", "windows", "ubuntu", "linux", "unknown" and
            platform_detail provides additional context (e.g. "Apple Silicon").
        """
        system = platform.system().lower()
        if system == "darwin":
            machine = platform.machine()
            detail = "Apple Silicon" if machine == "arm64" else "Intel"
            return "mac", detail
        elif system == "windows":
            return "windows", platform.version()
        elif system == "linux":
            try:
                with open("/etc/os-release", "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    if "ubuntu" in content:
                        return "ubuntu", platform.version()
            except OSError:
                pass
            return "linux", platform.version()
        return "unknown", ""

    def get_installed_version(self, tool_name: str) -> str | None:
        """Get the installed version of a command-line tool.

        Runs `<tool_name> --version` and returns the first line of output.

        Args:
            tool_name: Name of the tool (e.g. "git", "node", "python3").

        Returns:
            Version string from the tool, or None if the tool is not found
            or the version command fails.
        """
        if not shutil.which(tool_name):
            return None
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            output = result.stdout.strip() or result.stderr.strip()
            # Return the first line only
            return output.split("\n")[0] if output else None
        except (subprocess.SubprocessError, OSError):
            return None

    def get_env(self, key: str, default: str = "") -> str:
        """Read an environment variable.

        Args:
            key: Variable name.
            default: Default value if the variable is not set.

        Returns:
            The variable's value, or the default.
        """
        return os.environ.get(key, default)

    def set_env(self, key: str, value: str) -> None:
        """Set an environment variable in the current process.

        Args:
            key: Variable name.
            value: Value to set.
        """
        os.environ[key] = value

    def get_all_proxy_vars(self) -> dict[str, str]:
        """Read all proxy-related environment variables.

        Returns:
            Dict of proxy variable names to their values. Only includes
            variables that are actually set.
        """
        proxy_keys = [
            "HTTP_PROXY",
            "http_proxy",
            "HTTPS_PROXY",
            "https_proxy",
            "NO_PROXY",
            "no_proxy",
            "ALL_PROXY",
            "all_proxy",
        ]
        return {key: os.environ[key] for key in proxy_keys if key in os.environ}

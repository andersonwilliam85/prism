"""SystemAccessor — platform detection, OS info, and environment variables.

Pure I/O translation: wraps platform module, /etc/os-release,
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
        """Detect the current operating system."""
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
        """Get the installed version of a command-line tool."""
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
            return output.split("\n")[0] if output else None
        except (subprocess.SubprocessError, OSError):
            return None

    def get_env(self, key: str, default: str = "") -> str:
        """Read an environment variable."""
        return os.environ.get(key, default)

    def set_env(self, key: str, value: str) -> None:
        """Set an environment variable in the current process."""
        os.environ[key] = value

    def get_all_proxy_vars(self) -> dict[str, str]:
        """Read all proxy-related environment variables."""
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

"""Platform detection utility.

Extracted from installer_engine.py:194-210. Pure logic — no I/O except
reading /etc/os-release (which is a static file, not a service boundary).
"""

from __future__ import annotations

import platform


def detect_platform() -> tuple[str, str]:
    """Detect OS and return (platform_name, platform_detail).

    Returns:
        ("mac", "Apple Silicon") | ("mac", "Intel")
        ("windows", version)
        ("ubuntu", version) | ("linux", version)
        ("unknown", "")
    """
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

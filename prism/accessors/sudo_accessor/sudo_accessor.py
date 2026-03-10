"""SudoAccessor — subprocess boundary for sudo validation.

Validates sudo credentials via `sudo -S -v`. The password is passed
via stdin (never appears in process args or logs).

Volatility: low — sudo -S -v is POSIX-stable.
"""

from __future__ import annotations

import shutil
import subprocess


class SudoAccessor:
    """Concrete implementation of ISudoAccessor."""

    def validate_password(self, password: str) -> bool:
        """Validate a sudo password via sudo -S -v.

        The password is piped to stdin. Never logged or stored.
        Returns True if validation succeeds.
        """
        try:
            result = subprocess.run(
                ["sudo", "-S", "-v"],
                input=password + "\n",
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def is_sudo_available(self) -> bool:
        """Check if sudo is available on this system."""
        return shutil.which("sudo") is not None

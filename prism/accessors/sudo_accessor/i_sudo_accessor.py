"""ISudoAccessor — I/O boundary for sudo password validation.

Wraps the subprocess call to validate sudo credentials.
This is the only place that touches the actual system sudo.

Volatility: low — sudo validation mechanism is OS-stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ISudoAccessor(Protocol):
    def validate_password(self, password: str) -> bool:
        """Validate a sudo password via the system.

        Returns True if the password is correct, False otherwise.
        The password is never stored or logged.
        """
        ...

    def is_sudo_available(self) -> bool:
        """Check if sudo is available on this system."""
        ...

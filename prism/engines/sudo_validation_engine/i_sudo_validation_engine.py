"""ISudoValidationEngine — pure logic for sudo session management.

Handles token generation, TTL validation, attempt tracking, and lockout.
No subprocess calls — those belong in the accessor.

Volatility: low — session lifecycle logic is stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import SudoSession


@runtime_checkable
class ISudoValidationEngine(Protocol):
    def create_session(self) -> SudoSession:
        """Create a new sudo session with a fresh token."""
        ...

    def validate_session(self, session: SudoSession) -> bool:
        """Check if a session is still valid (not expired, not locked)."""
        ...

    def record_attempt(self, session: SudoSession, success: bool) -> SudoSession:
        """Record a password attempt. Locks session after max_attempts failures."""
        ...

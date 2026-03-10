"""SudoValidationEngine — pure logic for sudo session management.

Generates tokens, tracks attempts, enforces TTL and lockout.
All I/O (actual sudo validation) is in the SudoAccessor.

Volatility: low — session lifecycle logic is stable.
"""

from __future__ import annotations

import secrets
from dataclasses import replace
from datetime import datetime, timedelta

from prism.models.installation import SudoSession

_LOCKOUT_SECONDS = 30


class SudoValidationEngine:
    """Concrete implementation of ISudoValidationEngine."""

    def create_session(self) -> SudoSession:
        """Create a new sudo session with a cryptographically random token."""
        return SudoSession(token=secrets.token_urlsafe(32))

    def validate_session(self, session: SudoSession) -> bool:
        """Check if a session is still valid (not expired, not locked)."""
        if session.is_expired:
            return False
        if session.is_locked:
            return False
        return True

    def record_attempt(self, session: SudoSession, success: bool) -> SudoSession:
        """Record a password attempt.

        On success: resets attempt counter.
        On failure: increments counter, locks after max_attempts with 30s backoff.
        """
        if success:
            return replace(session, attempts=0, locked_until=None)

        new_attempts = session.attempts + 1
        locked_until = None
        if new_attempts >= session.max_attempts:
            locked_until = datetime.now() + timedelta(seconds=_LOCKOUT_SECONDS)

        return replace(session, attempts=new_attempts, locked_until=locked_until)

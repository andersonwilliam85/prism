"""IRollbackAccessor — I/O boundary for rollback state persistence.

Persists rollback state to a temp file so it survives process crashes.
Also executes rollback commands (file deletion, command execution).

Volatility: low — file I/O and command execution are stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import RollbackState


@runtime_checkable
class IRollbackAccessor(Protocol):
    def save_state(self, state: RollbackState) -> str:
        """Persist rollback state to a temp file. Returns the file path."""
        ...

    def load_state(self, path: str) -> RollbackState | None:
        """Load rollback state from a temp file. Returns None if not found."""
        ...

    def delete_file(self, path: str) -> bool:
        """Delete a file. Returns True if deleted, False if not found."""
        ...

    def delete_directory(self, path: str) -> bool:
        """Delete a directory tree. Returns True if deleted."""
        ...

    def run_command(self, command: str) -> tuple[bool, str]:
        """Run a rollback command. Returns (success, output)."""
        ...

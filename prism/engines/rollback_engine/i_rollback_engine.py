"""IRollbackEngine — pure logic for installation rollback.

Tracks install actions, computes LIFO undo sequences, validates
rollback completeness. No I/O — actual file/command execution
is done by the accessor layer.

Volatility: low — rollback logic is stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import RollbackAction, RollbackState


@runtime_checkable
class IRollbackEngine(Protocol):
    def create_state(self, package_name: str) -> RollbackState:
        """Create a fresh rollback state for an installation."""
        ...

    def record_action(
        self,
        state: RollbackState,
        action_type: str,
        target: str,
        rollback_command: str = "",
        original_value: str = "",
    ) -> None:
        """Record an action that may need to be undone."""
        ...

    def compute_rollback_plan(self, state: RollbackState) -> list[RollbackAction]:
        """Compute the LIFO rollback sequence. Filters out no-op actions."""
        ...

    def validate_completeness(self, state: RollbackState) -> tuple[bool, list[str]]:
        """Check if all actions have a rollback path. Returns (ok, warnings)."""
        ...

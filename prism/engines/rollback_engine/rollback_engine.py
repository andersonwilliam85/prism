"""RollbackEngine — pure logic for installation rollback.

Tracks actions, computes LIFO undo sequences, validates completeness.
All I/O is delegated to the accessor/manager layer.

Volatility: low — rollback logic is stable.
"""

from __future__ import annotations

from prism.models.installation import RollbackAction, RollbackState

# Action types that can auto-generate rollback without explicit commands
_AUTO_ROLLBACK_TYPES = {"file_created", "dir_created"}

# Action types that require explicit rollback commands
_EXPLICIT_ROLLBACK_TYPES = {"command_executed", "package_installed"}


class RollbackEngine:
    """Concrete implementation of IRollbackEngine."""

    def create_state(self, package_name: str) -> RollbackState:
        """Create a fresh rollback state for an installation."""
        return RollbackState(package_name=package_name)

    def record_action(
        self,
        state: RollbackState,
        action_type: str,
        target: str,
        rollback_command: str = "",
        original_value: str = "",
    ) -> None:
        """Record an action that may need to be undone."""
        action = RollbackAction(
            action_type=action_type,
            target=target,
            rollback_command=rollback_command,
            original_value=original_value,
        )
        state.record(action)

    def compute_rollback_plan(self, state: RollbackState) -> list[RollbackAction]:
        """Compute the LIFO rollback sequence.

        Filters out actions that have no rollback path and no auto-rollback
        capability (e.g., config_changed with no original_value).
        """
        plan = []
        for action in state.undo_sequence():
            if action.rollback_command:
                plan.append(action)
            elif action.action_type in _AUTO_ROLLBACK_TYPES:
                plan.append(action)
            elif action.action_type == "config_changed" and action.original_value:
                plan.append(action)
            # Skip actions with no rollback path
        return plan

    def validate_completeness(self, state: RollbackState) -> tuple[bool, list[str]]:
        """Check if all actions have a rollback path.

        Returns (all_covered, list_of_warnings).
        """
        warnings: list[str] = []
        for action in state.actions:
            if action.rollback_command:
                continue
            if action.action_type in _AUTO_ROLLBACK_TYPES:
                continue
            if action.action_type == "config_changed" and action.original_value:
                continue
            warnings.append(f"No rollback for {action.action_type}: {action.target}")
        return len(warnings) == 0, warnings

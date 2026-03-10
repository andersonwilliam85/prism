"""Rollback planning and execution — private submodule.

Handles computing rollback plans from state and executing undo actions
via the rollback accessor.
"""

from __future__ import annotations

from prism.accessors.command_accessor.i_command_accessor import ICommandAccessor
from prism.accessors.rollback_accessor.i_rollback_accessor import IRollbackAccessor
from prism.models.installation import RollbackAction, RollbackState

_AUTO_ROLLBACK_TYPES = {"file_created", "dir_created"}


def compute_rollback_plan(state: RollbackState) -> list[RollbackAction]:
    """Compute which actions can be rolled back (LIFO order)."""
    plan = []
    for action in state.undo_sequence():
        if action.rollback_command:
            plan.append(action)
        elif action.action_type in _AUTO_ROLLBACK_TYPES:
            plan.append(action)
        elif action.action_type == "config_changed" and action.original_value:
            plan.append(action)
    return plan


def execute_rollback(
    state: RollbackState,
    rollback_accessor: IRollbackAccessor,
    command_accessor: ICommandAccessor,
    log_fn,
) -> list[dict]:
    """Execute rollback for the given state, returning results."""
    plan = compute_rollback_plan(state)
    results: list[dict] = []

    for action in plan:
        log_fn("rollback", f"Undoing {action.action_type}: {action.target}")
        try:
            if action.rollback_command:
                ok, output = rollback_accessor.run_command(action.rollback_command)
                results.append({"action": action.target, "success": ok, "detail": output})
            elif action.action_type == "file_created":
                ok = rollback_accessor.delete_file(action.target)
                results.append({"action": action.target, "success": ok, "detail": "deleted" if ok else "not found"})
            elif action.action_type == "dir_created":
                ok = rollback_accessor.delete_directory(action.target)
                results.append({"action": action.target, "success": ok, "detail": "deleted" if ok else "not found"})
            elif action.action_type == "config_changed" and action.original_value:
                command_accessor.git_set_config(action.target, action.original_value, scope="global")
                results.append({"action": action.target, "success": True, "detail": "restored"})
            else:
                results.append({"action": action.target, "success": False, "detail": "no rollback path"})
        except Exception as e:
            results.append({"action": action.target, "success": False, "detail": str(e)})

        level = "success" if results[-1]["success"] else "warning"
        log_fn("rollback", f"  → {results[-1]['detail']}", level)

    state.rolled_back = True
    return results

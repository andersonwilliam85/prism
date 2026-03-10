"""IInstallationEngine — execute installation, rollback, and preflight checks.

Coarse-grained interface for the installation surface volatility axis.
The manager says "install with this context" — the engine handles everything:
git config, workspace dirs, repo clones, tool installs, SSH keys, rollback.

Volatility: low-medium — installation surface evolves slowly.
"""

from __future__ import annotations

import threading
from typing import Protocol, runtime_checkable

from prism.models.installation import (
    InstallationResult,
    InstallContext,
    PrivilegedStep,
    ProgressCallback,
    RollbackState,
)


@runtime_checkable
class IInstallationEngine(Protocol):
    def install(self, context: InstallContext) -> InstallationResult:
        """Execute the full installation pipeline.

        The engine owns all steps: preflight, git config, workspace,
        repos, tools, config files, finalization. It calls accessors
        internally for both reads and writes.
        """
        ...

    def install_privileged(self, steps: list[PrivilegedStep], platform_name: str) -> InstallationResult:
        """Execute deferred privileged install steps (Phase 2)."""
        ...

    def rollback(self, state: RollbackState | None = None) -> list[dict]:
        """Execute rollback for the given or current state."""
        ...

    def set_cancel_event(self, event: threading.Event) -> None:
        """Set a threading Event that signals cancellation."""
        ...

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """Set a callback for progress reporting."""
        ...

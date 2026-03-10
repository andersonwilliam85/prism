"""Installation plan and result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class InstallationPlan:
    """What will be installed — computed before execution."""

    package_name: str
    tools: list[str] = field(default_factory=list)
    repos: list[str] = field(default_factory=list)
    directories: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    selected_tiers: dict[str, str] = field(default_factory=dict)


@dataclass
class StepResult:
    step: str
    success: bool
    message: str = ""
    skipped: bool = False


@dataclass
class PrivilegedStep:
    """A step that requires elevated privileges (sudo/admin)."""

    name: str
    command: str
    needs_sudo: bool = True
    platform: str = ""


@dataclass
class RollbackAction:
    """A tracked action that can be undone during rollback.

    Each install step records what it did so rollback can undo it in LIFO order.
    """

    action_type: str  # file_created, dir_created, command_executed, config_changed, package_installed
    target: str  # file/dir path or package name
    rollback_command: str = ""  # explicit undo command (from package.yaml or auto-generated)
    original_value: str = ""  # for config changes: the value before modification
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RollbackState:
    """Tracks all actions for a single installation — enables LIFO undo."""

    package_name: str
    actions: list[RollbackAction] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    rolled_back: bool = False

    def record(self, action: RollbackAction) -> None:
        """Record an action for potential rollback."""
        self.actions.append(action)

    def undo_sequence(self) -> list[RollbackAction]:
        """Return actions in LIFO order for rollback."""
        return list(reversed(self.actions))


@dataclass
class SudoSession:
    """A time-limited sudo validation session.

    Created when the user successfully validates their password.
    Expires after ttl_seconds (default 15 minutes). The token is
    opaque and memory-only — never logged or persisted.
    """

    token: str
    created_at: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 900  # 15 minutes
    attempts: int = 0
    max_attempts: int = 3
    locked_until: datetime | None = None

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)

    @property
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until


@dataclass
class InstallationResult:
    """Outcome of a full installation run."""

    success: bool
    package_name: str
    steps: list[StepResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None
    error: str | None = None
    pending_privileged: list[PrivilegedStep] = field(default_factory=list)
    phase: int = 0

"""IPreflightManager — orchestrates environment prerequisite checking.

Volatility: low — check sequence and pass/fail criteria are stable.
Separate from InstallationManager because preflight can run
independently (e.g., UI "is my machine ready?" preview).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IPreflightManager(Protocol):
    def check(self, requirements: dict) -> tuple[bool, list[str]]: ...

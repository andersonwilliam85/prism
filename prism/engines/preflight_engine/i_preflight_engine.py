"""IPreflightEngine — version comparison, requires checking.

Volatility: low — comparison logic rarely changes.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IPreflightEngine(Protocol):
    def check_requirements(self, requirements: dict, installed_versions: dict[str, str]) -> tuple[bool, list[str]]: ...

    def version_satisfies(self, installed: str, required: str) -> bool: ...

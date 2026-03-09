"""IResolutionEngine — resolve package source (local, npm, url).

Volatility: medium — changes as new source types are supported.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IResolutionEngine(Protocol):
    def resolve(self, package_name: str, sources: list[dict] | None = None) -> dict: ...

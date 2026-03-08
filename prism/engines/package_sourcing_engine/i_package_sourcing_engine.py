"""IPackageSourcingEngine — resolve local vs remote prism source.

Volatility: medium — changes as new registry/source types are supported.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IPackageSourcingEngine(Protocol):
    def resolve(self, package_name: str, sources: list[dict] | None = None) -> dict: ...

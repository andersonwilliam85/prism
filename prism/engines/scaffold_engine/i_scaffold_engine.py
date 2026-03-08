"""IScaffoldEngine — template generation for new prisms.

Volatility: low — scaffold structure is stable once established.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IScaffoldEngine(Protocol):
    def generate(self, name: str, template: str = "basic") -> dict[str, str]: ...

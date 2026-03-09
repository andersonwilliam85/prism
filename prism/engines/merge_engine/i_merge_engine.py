"""IMergeEngine — deep merge strategies for config dictionaries.

Volatility: high — merge rules change as prism schema evolves.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IMergeEngine(Protocol):
    def merge(self, base: dict, override: dict) -> dict: ...

    def merge_tiers(self, base_config: dict, tier_configs: list[dict]) -> dict: ...

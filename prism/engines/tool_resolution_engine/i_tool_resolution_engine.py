"""IToolResolutionEngine — tools_selected/excluded filtering, platform dispatch.

Volatility: medium — changes when new platforms or tool categories added.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IToolResolutionEngine(Protocol):
    def resolve(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> list[dict]: ...

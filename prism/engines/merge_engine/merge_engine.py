"""MergeEngine — deep merge config dictionaries with tier merging.

Extracted from scripts/config_merger.py. Pure computation — no I/O.

Volatility: high — merge rules change as prism schema evolves.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

_DEFAULT_RULES: dict = {
    "merge_strategy": {
        "arrays": {
            "tools_required": "union",
            "tools_selected": "union",
            "tools_excluded": "union",
            "repositories": "append",
            "resources": "append",
            "onboarding_tasks": "append",
        },
        "objects": {
            "environment": "deep_merge",
            "git": "override",
            "career": "user_only",
            "tools": "deep_merge",
        },
        "conflicts": {"default": "override"},
    }
}


class MergeEngine:
    """Deep merge config dictionaries with configurable strategies.

    Supports array strategies (union, append, override),
    object strategies (deep_merge, override, user_only),
    and tier-based sequential merging.
    """

    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules if rules is not None else deepcopy(_DEFAULT_RULES)

    def merge(self, base: dict, override: dict) -> dict:
        """Merge override into base, returning a new dict."""
        return self._merge_level(base, override, level="override")

    def merge_tiers(self, base_config: dict, tier_configs: list[dict]) -> dict:
        """Sequentially merge a list of tier configs onto a base config."""
        result = deepcopy(base_config)
        for tier_config in tier_configs:
            result = self._merge_level(result, tier_config, level="tier")
        return result

    # ------------------------------------------------------------------
    # Internal merge logic
    # ------------------------------------------------------------------

    def _merge_level(self, base: dict, overlay: dict, level: str) -> dict:
        result = deepcopy(base)
        for key, value in overlay.items():
            if key not in result:
                result[key] = deepcopy(value)
            else:
                result[key] = self._merge_value(key, result[key], value, level)
        return result

    def _merge_value(self, key: str, base_value: Any, overlay_value: Any, level: str) -> Any:
        strategy = self._get_object_strategy(key)

        if isinstance(base_value, dict) and isinstance(overlay_value, dict):
            explicit_strategies = self._rules.get("merge_strategy", {}).get("objects", {})
            if strategy == "user_only" and level != "user":
                return deepcopy(base_value)
            elif key in explicit_strategies and strategy == "override":
                return deepcopy(overlay_value)
            else:
                return self._deep_merge_dicts(base_value, overlay_value)

        if isinstance(base_value, list) and isinstance(overlay_value, list):
            array_strategy = self._get_array_strategy(key)
            if array_strategy == "union":
                try:
                    return list(set(base_value + overlay_value))
                except TypeError:
                    seen: list = []
                    for item in base_value + overlay_value:
                        if item not in seen:
                            seen.append(item)
                    return seen
            elif array_strategy == "append":
                return base_value + overlay_value
            else:
                return deepcopy(overlay_value)

        return deepcopy(overlay_value)

    def _get_object_strategy(self, key: str) -> str:
        strategies = self._rules.get("merge_strategy", {}).get("objects", {})
        default = self._rules.get("merge_strategy", {}).get("conflicts", {}).get("default", "override")
        return strategies.get(key, default)

    def _get_array_strategy(self, key: str) -> str:
        strategies = self._rules.get("merge_strategy", {}).get("arrays", {})
        return strategies.get(key, "override")

    def _deep_merge_dicts(self, base: dict, overlay: dict) -> dict:
        result = deepcopy(base)
        for key, value in overlay.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = deepcopy(value)
            else:
                result[key] = deepcopy(value)
        return result

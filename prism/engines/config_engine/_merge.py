"""Deep merge logic and strategies — private submodule of ConfigEngine.

Pure functions that operate on dicts with a rules configuration.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULT_RULES: dict = {
    "merge_strategy": {
        "arrays": {
            "tools_required": "union",
            "tools_optional": "union",
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


def merge_level(base: dict, overlay: dict, level: str, rules: dict) -> dict:
    """Merge overlay into base at the given level, returning a new dict."""
    result = deepcopy(base)
    for key, value in overlay.items():
        if key not in result:
            result[key] = deepcopy(value)
        else:
            result[key] = merge_value(key, result[key], value, level, rules)
    return result


def merge_value(key: str, base_value: Any, overlay_value: Any, level: str, rules: dict) -> Any:
    """Merge a single value according to strategy rules."""
    strategy = _get_object_strategy(key, rules)

    if isinstance(base_value, dict) and isinstance(overlay_value, dict):
        explicit_strategies = rules.get("merge_strategy", {}).get("objects", {})
        if strategy == "user_only" and level != "user":
            return deepcopy(base_value)
        elif key in explicit_strategies and strategy == "override":
            return deepcopy(overlay_value)
        else:
            return deep_merge_dicts(base_value, overlay_value)

    if isinstance(base_value, list) and isinstance(overlay_value, list):
        array_strategy = _get_array_strategy(key, rules)
        if array_strategy == "union":
            try:
                return list(set(base_value + overlay_value))
            except TypeError:
                # For tool lists: deduplicate by name, prefer dict over string,
                # and prefer the entry with more detail
                seen_names: dict = {}
                for item in base_value + overlay_value:
                    name = item.get("name") if isinstance(item, dict) else item if isinstance(item, str) else None
                    if name is None:
                        continue
                    existing = seen_names.get(name)
                    if existing is None:
                        seen_names[name] = item
                    elif isinstance(item, dict) and not isinstance(existing, dict):
                        seen_names[name] = item
                    elif isinstance(item, dict) and isinstance(existing, dict):
                        # Merge: overlay wins for each key
                        merged = dict(existing)
                        merged.update(item)
                        seen_names[name] = merged
                return list(seen_names.values())
        elif array_strategy == "append":
            return base_value + overlay_value
        else:
            return deepcopy(overlay_value)

    return deepcopy(overlay_value)


def deep_merge_dicts(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay into base."""
    result = deepcopy(base)
    for key, value in overlay.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_dicts(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                result[key] = result[key] + value
            else:
                result[key] = deepcopy(value)
        else:
            result[key] = deepcopy(value)
    return result


def _get_object_strategy(key: str, rules: dict) -> str:
    strategies = rules.get("merge_strategy", {}).get("objects", {})
    default = rules.get("merge_strategy", {}).get("conflicts", {}).get("default", "override")
    return strategies.get(key, default)


def _get_array_strategy(key: str, rules: dict) -> str:
    strategies = rules.get("merge_strategy", {}).get("arrays", {})
    return strategies.get(key, "override")

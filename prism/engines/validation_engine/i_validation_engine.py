"""IValidationEngine — prism schema validation, field checks.

Volatility: medium — new schema fields require new validation rules.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IValidationEngine(Protocol):
    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]: ...

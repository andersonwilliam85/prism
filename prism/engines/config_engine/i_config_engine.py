"""IConfigEngine — validate, merge, and resolve config hierarchies.

Coarse-grained interface for the schema evolution volatility axis.
Owns config validation (schema-specific), merge strategies, and field hierarchy.

Volatility: medium-high — schema fields, merge rules, and validation rules co-evolve.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.package_info import UserField


@runtime_checkable
class IConfigEngine(Protocol):
    # --- Validation ---

    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]:
        """Validate a prism config dict.

        Returns (is_valid, errors, warnings).
        """
        ...

    # --- Validate + Merge (convenience) ---

    def prepare(
        self,
        config: dict,
        tier_configs: list[dict] | None = None,
    ) -> tuple[bool, dict, list[str], list[str]]:
        """Validate and merge a prism config with its tier overrides.

        Returns (is_valid, merged_config, errors, warnings).
        """
        ...

    # --- Merge ---

    def merge(self, base: dict, override: dict) -> dict:
        """Merge override into base, returning a new dict."""
        ...

    def merge_tiers(self, base_config: dict, tier_configs: list[dict]) -> dict:
        """Sequentially merge a list of tier configs onto a base config."""
        ...

    # --- Field hierarchy ---

    def resolve_dependency_order(self, fields: list[UserField]) -> list[UserField]:
        """Sort fields so parents appear before dependents."""
        ...

    def filter_options(self, field: UserField, parent_value: str) -> list[str]:
        """Return filtered options for a dependent field given parent value."""
        ...

    def get_dependent_fields(self, field_id: str, fields: list[UserField]) -> list[UserField]:
        """Return fields that directly depend on field_id."""
        ...

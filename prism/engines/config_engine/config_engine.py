"""ConfigEngine — schema validation, deep merge, and field hierarchy resolution.

Consolidates MergeEngine + ValidationEngine + HierarchyEngine into a single
engine aligned to the schema evolution volatility axis.

Volatility: medium-high — merge rules, validation rules, and field hierarchy
logic all change when package.yaml schema evolves.
"""

from __future__ import annotations

from copy import deepcopy

from prism.models.package_info import UserField

from . import _merge, _validators


class ConfigEngine:
    """Unified config engine: validate, merge, and resolve field hierarchies.

    All three concerns share the schema evolution volatility axis —
    when package.yaml schema changes, validation rules, merge strategies,
    and field dependency logic change together.
    """

    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules if rules is not None else deepcopy(_merge.DEFAULT_RULES)

    # ==================================================================
    # Public — coarse-grained interface
    # ==================================================================

    def prepare(
        self,
        config: dict,
        tier_configs: list[dict] | None = None,
    ) -> tuple[bool, dict, list[str], list[str]]:
        """Validate and merge a prism config with its tier overrides.

        Returns (is_valid, merged_config, errors, warnings).
        """
        is_valid, errors, warnings = self.validate(config)
        if not is_valid:
            return False, {}, errors, warnings

        merged = config
        if tier_configs:
            merged = self.merge_tiers(config, tier_configs)

        return True, merged, errors, warnings

    # ==================================================================
    # Validation — dispatches to _validators submodule
    # ==================================================================

    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]:
        """Validate a parsed prism config dict.

        Returns (is_valid, errors, warnings).
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not config:
            errors.append("Config is empty")
            return False, errors, warnings

        _validators.validate_package_section(config, errors, warnings)
        _validators.validate_install_configuration(config, warnings)

        prism_config = config.get("prism_config", {})
        if prism_config:
            _validators.validate_prism_config(prism_config, errors, warnings)

        bundled = config.get("bundled_prisms", {})
        if bundled:
            _validators.validate_bundled_prisms(bundled, errors, warnings)

        user_fields = config.get("user_info_fields") or config.get("package", {}).get("user_info_fields", [])
        if user_fields:
            _validators.validate_user_info_fields(user_fields, errors, warnings)
        else:
            warnings.append("No user_info_fields defined — will use defaults")

        _validators.validate_metadata(config, errors)

        registry = config.get("tool_registry", {})
        if registry:
            _validators.validate_tool_registry(registry, errors, warnings)
            _validators.validate_tool_references(config, registry, errors, warnings)

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    # ==================================================================
    # Merge — delegates to _merge submodule
    # ==================================================================

    def merge(self, base: dict, override: dict) -> dict:
        """Merge override into base, returning a new dict."""
        return _merge.merge_level(base, override, level="override", rules=self._rules)

    def merge_tiers(self, base_config: dict, tier_configs: list[dict]) -> dict:
        """Sequentially merge a list of tier configs onto a base config."""
        result = deepcopy(base_config)
        for tier_config in tier_configs:
            result = _merge.merge_level(result, tier_config, level="tier", rules=self._rules)
        return result

    # ==================================================================
    # Field hierarchy
    # ==================================================================

    def filter_options(self, field: UserField, parent_value: str) -> list[str]:
        """Return filtered options for a dependent field given parent value."""
        if not field.option_map or not parent_value:
            return field.options
        return field.option_map.get(parent_value, field.options)

    def resolve_dependency_order(self, fields: list[UserField]) -> list[UserField]:
        """Sort fields so parents appear before dependents (topological sort)."""
        field_by_id = {f.id: f for f in fields}
        visited: set[str] = set()
        result: list[UserField] = []

        def visit(fid: str) -> None:
            if fid in visited:
                return
            visited.add(fid)
            f = field_by_id.get(fid)
            if f is None:
                return
            if f.depends_on and f.depends_on in field_by_id:
                visit(f.depends_on)
            result.append(f)

        for f in fields:
            visit(f.id)

        return result

    def get_dependent_fields(self, field_id: str, fields: list[UserField]) -> list[UserField]:
        """Return fields that directly depend on field_id."""
        return [f for f in fields if f.depends_on == field_id]

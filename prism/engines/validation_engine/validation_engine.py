"""ValidationEngine — validate prism package.yaml config dicts.

Extracted from scripts/package_validator.py. Pure computation — no I/O.

Volatility: medium — new schema fields require new validation rules.
"""

from __future__ import annotations

VALID_FIELD_TYPES = {"text", "email", "url", "select", "number", "checkbox"}
REQUIRED_PACKAGE_FIELDS = ["name", "version", "description"]


class ValidationEngine:
    """Validate a prism config dict (parsed package.yaml content)."""

    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]:
        """Validate a parsed prism config dict.

        Returns:
            (is_valid, errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not config:
            errors.append("Config is empty")
            return False, errors, warnings

        if "package" not in config:
            errors.append("Missing required top-level key: 'package'")
        else:
            pkg = config["package"]
            if not isinstance(pkg, dict):
                errors.append("'package' must be a dictionary")
            else:
                for field in REQUIRED_PACKAGE_FIELDS:
                    if field not in pkg:
                        errors.append(f"Missing required field: package.{field}")
                    elif not pkg[field]:
                        errors.append(f"Empty required field: package.{field}")

        has_bundled_prisms = "bundled_prisms" in config
        has_legacy_install = isinstance(config.get("package", {}), dict) and "install" in config.get("package", {})
        has_setup = "setup" in config and "install" in config.get("setup", {})

        if not has_bundled_prisms and not has_legacy_install and not has_setup:
            warnings.append(
                "No 'bundled_prisms' or install configuration found — "
                "prism has no sub-prisms and no file installation steps"
            )

        prism_config = config.get("prism_config", {})
        if prism_config:
            self._validate_prism_config(prism_config, errors, warnings)

        bundled = config.get("bundled_prisms", {})
        if bundled:
            self._validate_bundled_prisms(bundled, errors, warnings)

        user_fields = config.get("user_info_fields") or config.get("package", {}).get("user_info_fields", [])
        if user_fields:
            self._validate_user_info_fields(user_fields, errors, warnings)
        else:
            warnings.append("No user_info_fields defined — will use defaults")

        if "metadata" in config:
            metadata = config["metadata"]
            if not isinstance(metadata, dict):
                errors.append("'metadata' must be a dictionary")
            elif "tags" in metadata and not isinstance(metadata["tags"], list):
                errors.append("'metadata.tags' must be a list")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def _validate_prism_config(self, prism_config: dict, errors: list[str], warnings: list[str]) -> None:
        # Theme is validated only for type — packages define their own themes
        theme = prism_config.get("theme")
        if theme and not isinstance(theme, str):
            errors.append("'prism_config.theme' must be a string")

        sources = prism_config.get("sources", [])
        if sources and not isinstance(sources, list):
            errors.append("'prism_config.sources' must be a list")

    def _validate_bundled_prisms(self, bundled: dict, errors: list[str], warnings: list[str]) -> None:
        if not isinstance(bundled, dict):
            errors.append("'bundled_prisms' must be a dictionary of tiers")
            return

        for tier_name, tier_items in bundled.items():
            if not isinstance(tier_items, list):
                errors.append(f"'bundled_prisms.{tier_name}' must be a list")
                continue

            for idx, item in enumerate(tier_items):
                if not isinstance(item, dict):
                    errors.append(f"'bundled_prisms.{tier_name}[{idx}]' must be a dictionary")
                    continue
                if "id" not in item:
                    errors.append(f"'bundled_prisms.{tier_name}[{idx}]' missing 'id'")
                if "config" not in item:
                    errors.append(f"'bundled_prisms.{tier_name}[{idx}]' missing 'config'")

    def _validate_user_info_fields(self, user_fields: list, errors: list[str], warnings: list[str]) -> None:
        if not isinstance(user_fields, list):
            errors.append("'user_info_fields' must be a list")
            return

        for idx, field in enumerate(user_fields):
            if not isinstance(field, dict):
                errors.append(f"user_info_fields[{idx}] must be a dictionary")
                continue
            if "id" not in field:
                errors.append(f"user_info_fields[{idx}] missing 'id'")
            if "label" not in field:
                errors.append(f"user_info_fields[{idx}] missing 'label'")
            if "type" not in field:
                errors.append(f"user_info_fields[{idx}] missing 'type'")
            elif field["type"] not in VALID_FIELD_TYPES:
                warnings.append(
                    f"user_info_fields[{idx}] has unknown type '{field['type']}' — "
                    f"valid types: {', '.join(sorted(VALID_FIELD_TYPES))}"
                )

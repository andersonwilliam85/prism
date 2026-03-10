"""Config validation rules — private submodule of ConfigEngine.

Each validator receives the relevant config section and appends to
errors/warnings lists. The main validate() method dispatches here.
"""

from __future__ import annotations

VALID_FIELD_TYPES = {"text", "email", "url", "select", "number", "checkbox"}
REQUIRED_PACKAGE_FIELDS = ["name", "version", "description"]


def validate_package_section(config: dict, errors: list[str], warnings: list[str]) -> None:
    """Validate the top-level 'package' key."""
    if "package" not in config:
        errors.append("Missing required top-level key: 'package'")
        return

    pkg = config["package"]
    if not isinstance(pkg, dict):
        errors.append("'package' must be a dictionary")
        return

    for field in REQUIRED_PACKAGE_FIELDS:
        if field not in pkg:
            errors.append(f"Missing required field: package.{field}")
        elif not pkg[field]:
            errors.append(f"Empty required field: package.{field}")


def validate_install_configuration(config: dict, warnings: list[str]) -> None:
    """Warn when no install configuration is found."""
    has_bundled_prisms = "bundled_prisms" in config
    has_legacy_install = isinstance(config.get("package", {}), dict) and "install" in config.get("package", {})
    has_setup = "setup" in config and "install" in config.get("setup", {})

    if not has_bundled_prisms and not has_legacy_install and not has_setup:
        warnings.append(
            "No 'bundled_prisms' or install configuration found — "
            "prism has no sub-prisms and no file installation steps"
        )


def validate_prism_config(prism_config: dict, errors: list[str], warnings: list[str]) -> None:
    """Validate the prism_config section."""
    theme = prism_config.get("theme")
    if theme and not isinstance(theme, str):
        errors.append("'prism_config.theme' must be a string")

    sources = prism_config.get("sources", [])
    if sources and not isinstance(sources, list):
        errors.append("'prism_config.sources' must be a list")


def validate_bundled_prisms(bundled: dict, errors: list[str], warnings: list[str]) -> None:
    """Validate the bundled_prisms section."""
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


def validate_user_info_fields(user_fields: list, errors: list[str], warnings: list[str]) -> None:
    """Validate the user_info_fields section."""
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


def validate_metadata(config: dict, errors: list[str]) -> None:
    """Validate the optional metadata section."""
    metadata = config.get("metadata")
    if metadata is None:
        return
    if not isinstance(metadata, dict):
        errors.append("'metadata' must be a dictionary")
    elif "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append("'metadata.tags' must be a list")

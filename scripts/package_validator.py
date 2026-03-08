#!/usr/bin/env python3
"""
Prism Validator

Validates prism packages to ensure they have the required structure and fields.

A valid prism must have:
  - package.yaml that parses as valid YAML
  - A top-level `package:` section with name, version, description
  - Either `bundled_prisms:` (new format) or `package.install:` (legacy format)

Optional but validated when present:
  - prism_config: theme, sources, branding
  - bundled_prisms: each tier is a list of dicts with id, name, config
  - user_info_fields: each field has id, label, type
  - metadata: tags is a list
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

VALID_THEMES = {"ocean", "purple", "forest", "sunset", "midnight"}
VALID_FIELD_TYPES = {"text", "email", "url", "select", "number", "checkbox"}


class PrismValidator:
    """Validates prism packages"""

    REQUIRED_PACKAGE_FIELDS = ["name", "version", "description"]
    REQUIRED_TOP_LEVEL_KEYS = ["package"]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_package(self, package_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a prism directory.

        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        if not package_path.exists():
            self.errors.append(f"Prism directory does not exist: {package_path}")
            return False, self.errors, self.warnings

        if not package_path.is_dir():
            self.errors.append(f"Prism path is not a directory: {package_path}")
            return False, self.errors, self.warnings

        # Check for package.yaml
        package_yaml = package_path / "package.yaml"
        if not package_yaml.exists():
            self.errors.append("Missing required file: package.yaml")
            return False, self.errors, self.warnings

        # Parse YAML
        try:
            with open(package_yaml) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Failed to read package.yaml: {e}")
            return False, self.errors, self.warnings

        if not config:
            self.errors.append("package.yaml is empty")
            return False, self.errors, self.warnings

        # Validate top-level package: section
        if "package" not in config:
            self.errors.append("Missing required top-level key: 'package'")
        else:
            pkg = config["package"]
            if not isinstance(pkg, dict):
                self.errors.append("'package' must be a dictionary")
            else:
                for field in self.REQUIRED_PACKAGE_FIELDS:
                    if field not in pkg:
                        self.errors.append(f"Missing required field: package.{field}")
                    elif not pkg[field]:
                        self.errors.append(f"Empty required field: package.{field}")

        # Must have EITHER bundled_prisms (new format) OR package.install (legacy)
        has_bundled_prisms = "bundled_prisms" in config
        has_legacy_install = isinstance(config.get("package", {}), dict) and "install" in config.get("package", {})
        has_setup = "setup" in config and "install" in config.get("setup", {})

        if not has_bundled_prisms and not has_legacy_install and not has_setup:
            self.warnings.append(
                "No 'bundled_prisms' or install configuration found — "
                "prism has no sub-prisms and no file installation steps"
            )

        # Validate prism_config if present
        prism_config = config.get("prism_config", {})
        if prism_config:
            self._validate_prism_config(prism_config)

        # Validate bundled_prisms if present
        bundled = config.get("bundled_prisms", {})
        if bundled:
            self._validate_bundled_prisms(bundled, package_path)

        # Validate user_info_fields (can be at top level or inside package:)
        user_fields = config.get("user_info_fields") or config.get("package", {}).get("user_info_fields", [])
        if user_fields:
            self._validate_user_info_fields(user_fields)
        else:
            self.warnings.append("No user_info_fields defined — will use defaults")

        # README recommended
        if not (package_path / "README.md").exists():
            self.warnings.append("No README.md found (recommended)")

        # Validate metadata if present
        if "metadata" in config:
            metadata = config["metadata"]
            if not isinstance(metadata, dict):
                self.errors.append("'metadata' must be a dictionary")
            elif "tags" in metadata and not isinstance(metadata["tags"], list):
                self.errors.append("'metadata.tags' must be a list")

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_prism_config(self, prism_config: dict):
        """Validate the prism_config section."""
        theme = prism_config.get("theme")
        if theme and theme not in VALID_THEMES:
            self.warnings.append(f"Unknown theme '{theme}' — valid themes: {', '.join(sorted(VALID_THEMES))}")

        sources = prism_config.get("sources", [])
        if sources and not isinstance(sources, list):
            self.errors.append("'prism_config.sources' must be a list")

    def _validate_bundled_prisms(self, bundled: dict, package_path: Path):
        """Validate the bundled_prisms section and check referenced config files exist."""
        if not isinstance(bundled, dict):
            self.errors.append("'bundled_prisms' must be a dictionary of tiers")
            return

        for tier_name, tier_items in bundled.items():
            if not isinstance(tier_items, list):
                self.errors.append(f"'bundled_prisms.{tier_name}' must be a list")
                continue

            for idx, item in enumerate(tier_items):
                if not isinstance(item, dict):
                    self.errors.append(f"'bundled_prisms.{tier_name}[{idx}]' must be a dictionary")
                    continue

                if "id" not in item:
                    self.errors.append(f"'bundled_prisms.{tier_name}[{idx}]' missing 'id'")
                if "config" not in item:
                    self.errors.append(f"'bundled_prisms.{tier_name}[{idx}]' missing 'config'")
                else:
                    config_file = package_path / item["config"]
                    if not config_file.exists():
                        self.errors.append(
                            f"Sub-prism config not found: {item['config']} " f"(bundled_prisms.{tier_name}[{idx}])"
                        )

    def _validate_user_info_fields(self, user_fields: list):
        """Validate user_info_fields entries."""
        if not isinstance(user_fields, list):
            self.errors.append("'user_info_fields' must be a list")
            return

        for idx, field in enumerate(user_fields):
            if not isinstance(field, dict):
                self.errors.append(f"user_info_fields[{idx}] must be a dictionary")
                continue
            if "id" not in field:
                self.errors.append(f"user_info_fields[{idx}] missing 'id'")
            if "label" not in field:
                self.errors.append(f"user_info_fields[{idx}] missing 'label'")
            if "type" not in field:
                self.errors.append(f"user_info_fields[{idx}] missing 'type'")
            elif field["type"] not in VALID_FIELD_TYPES:
                self.warnings.append(
                    f"user_info_fields[{idx}] has unknown type '{field['type']}' — "
                    f"valid types: {', '.join(sorted(VALID_FIELD_TYPES))}"
                )

    def get_package_info(self, package_path: Path) -> Dict[str, Any]:
        """Extract basic prism info for display (works even on invalid prisms)."""
        try:
            package_yaml = package_path / "package.yaml"
            if not package_yaml.exists():
                return {
                    "id": package_path.name,
                    "name": package_path.name,
                    "version": "unknown",
                    "description": "No package.yaml found",
                    "error": True,
                }

            with open(package_yaml) as f:
                config = yaml.safe_load(f)

            if not config:
                return {
                    "id": package_path.name,
                    "name": package_path.name,
                    "version": "unknown",
                    "description": "Empty package.yaml",
                    "error": True,
                }

            pkg = config.get("package", {})
            return {
                "id": package_path.name,
                "name": pkg.get("name", package_path.name),
                "version": pkg.get("version", "unknown"),
                "description": pkg.get("description", "No description"),
                "type": pkg.get("type", "unknown"),
                "has_bundled_prisms": "bundled_prisms" in config,
                "theme": config.get("prism_config", {}).get("theme", "ocean"),
                "error": False,
            }
        except Exception as e:
            return {
                "id": package_path.name,
                "name": package_path.name,
                "version": "unknown",
                "description": f"Error: {e}",
                "error": True,
            }


def validate_all_packages(packages_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate all prisms in a directory.

    Returns:
        (valid_prisms, invalid_prisms)
    """
    validator = PrismValidator()
    valid_packages = []
    invalid_packages = []

    if not packages_dir.exists():
        return [], []

    for package_path in sorted(packages_dir.iterdir()):
        if not package_path.is_dir() or package_path.name.startswith("."):
            continue

        is_valid, errors, warnings = validator.validate_package(package_path)
        info = validator.get_package_info(package_path)

        package_data = {**info, "path": str(package_path), "errors": errors, "warnings": warnings}

        if is_valid:
            valid_packages.append(package_data)
        else:
            invalid_packages.append(package_data)

    return valid_packages, invalid_packages


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        package_path = Path(sys.argv[1])
    else:
        package_path = Path(__file__).parent.parent / "prisms"

    if package_path.is_dir() and (package_path / "package.yaml").exists():
        # Validate single prism
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(package_path)

        print(f"\n💎 Validating: {package_path.name}")
        print(f"\nValid: {is_valid}")

        if errors:
            print("\n❌ Errors:")
            for error in errors:
                print(f"  - {error}")

        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
    else:
        # Validate all prisms
        valid, invalid = validate_all_packages(package_path)

        print(f"\n💎 Prism Validation Results\n")
        print(f"✅ Valid:   {len(valid)}")
        print(f"❌ Invalid: {len(invalid)}")

        if valid:
            print("\n✅ Valid Prisms:")
            for pkg in valid:
                warnings_text = f" ({len(pkg['warnings'])} warnings)" if pkg["warnings"] else ""
                bundled = " [has sub-prisms]" if pkg.get("has_bundled_prisms") else ""
                print(f"  💎 {pkg['name']}{bundled}{warnings_text}")

        if invalid:
            print("\n❌ Invalid Prisms:")
            for pkg in invalid:
                print(f"\n  {pkg['name']}:")
                for error in pkg["errors"]:
                    print(f"    - {error}")

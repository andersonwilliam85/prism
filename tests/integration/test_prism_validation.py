"""
Integration tests — validate all real prisms in prisms/ directory.
Ensures every shipped prism is structurally valid according to PrismValidator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest  # noqa: E402
from package_validator import PrismValidator  # noqa: E402

PRISMS_DIR = Path(__file__).parent.parent.parent / "prisms"


def collect_prism_dirs():
    """Collect all prism directories for parametrize."""
    if not PRISMS_DIR.exists():
        return []
    return [
        d
        for d in sorted(PRISMS_DIR.iterdir())
        if d.is_dir() and not d.name.startswith(".") and (d / "package.yaml").exists()
    ]


@pytest.mark.integration
@pytest.mark.parametrize("prism_path", collect_prism_dirs(), ids=lambda p: p.name)
def test_real_prism_is_valid(prism_path):
    """Every prism in prisms/ must pass PrismValidator with no errors."""
    validator = PrismValidator()
    is_valid, errors, warnings = validator.validate_package(prism_path)

    # Show useful info on failure
    error_report = "\n".join(f"  ❌ {e}" for e in errors)
    warning_report = "\n".join(f"  ⚠️  {w}" for w in warnings)

    assert is_valid, f"Prism '{prism_path.name}' is invalid:\n{error_report}" + (
        f"\nWarnings:\n{warning_report}" if warnings else ""
    )


@pytest.mark.integration
def test_all_prisms_have_required_fields():
    """All prisms have name, version, description in the package: section."""
    for prism_path in collect_prism_dirs():
        import yaml

        data = yaml.safe_load((prism_path / "package.yaml").read_text())
        pkg = data.get("package", {})
        assert pkg.get("name"), f"{prism_path.name}: missing package.name"
        assert pkg.get("version"), f"{prism_path.name}: missing package.version"
        assert pkg.get("description"), f"{prism_path.name}: missing package.description"


@pytest.mark.integration
def test_all_prisms_have_at_least_one(collect_prism_dirs=collect_prism_dirs):
    """There must be at least one prism in the prisms/ directory."""
    prisms = collect_prism_dirs()
    assert len(prisms) > 0, f"No prisms found in {PRISMS_DIR}"


@pytest.mark.integration
def test_bundled_prisms_config_files_exist():
    """All config files referenced in bundled_prisms must exist on disk."""
    import yaml

    for prism_path in collect_prism_dirs():
        data = yaml.safe_load((prism_path / "package.yaml").read_text()) or {}
        bundled = data.get("bundled_prisms", {})
        for tier_name, tier_items in bundled.items():
            if not isinstance(tier_items, list):
                continue
            for item in tier_items:
                if not isinstance(item, dict):
                    continue
                config_file = item.get("config")
                if config_file:
                    config_path = prism_path / config_file
                    assert config_path.exists(), (
                        f"{prism_path.name}: missing config file '{config_file}' "
                        f"referenced in bundled_prisms.{tier_name}"
                    )


@pytest.mark.integration
def test_prism_themes_are_valid():
    """All prisms that specify a theme use a valid theme value."""
    import yaml
    from package_validator import VALID_THEMES

    for prism_path in collect_prism_dirs():
        data = yaml.safe_load((prism_path / "package.yaml").read_text()) or {}
        theme = data.get("prism_config", {}).get("theme")
        if theme:
            assert theme in VALID_THEMES, (
                f"{prism_path.name}: invalid theme '{theme}'. " f"Valid themes: {sorted(VALID_THEMES)}"
            )


@pytest.mark.integration
def test_user_info_field_types_are_valid():
    """All user_info_fields entries use valid type values."""
    import yaml
    from package_validator import VALID_FIELD_TYPES

    for prism_path in collect_prism_dirs():
        data = yaml.safe_load((prism_path / "package.yaml").read_text()) or {}
        fields = data.get("user_info_fields") or data.get("package", {}).get("user_info_fields", [])
        for field in fields or []:
            if isinstance(field, dict) and "type" in field:
                assert field["type"] in VALID_FIELD_TYPES, (
                    f"{prism_path.name}: field '{field.get('id')}' has invalid type '{field['type']}'. "
                    f"Valid: {sorted(VALID_FIELD_TYPES)}"
                )

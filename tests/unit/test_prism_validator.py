"""
Unit tests for PrismValidator.
"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from package_validator import VALID_FIELD_TYPES, VALID_THEMES, PrismValidator, validate_all_packages


@pytest.mark.unit
class TestPrismValidatorValid:
    """Tests for valid prism structures."""

    def test_valid_full_prism_passes(self, prism_dir):
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(prism_dir)
        assert is_valid, f"Expected valid but got errors: {errors}"
        assert len(errors) == 0

    def test_valid_minimal_prism_passes(self, temp_dir):
        pkg_dir = temp_dir / "minimal"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {
                        "name": "minimal-prism",
                        "version": "1.0.0",
                        "description": "Minimal valid prism",
                    }
                }
            )
        )
        (pkg_dir / "README.md").write_text("# Minimal\n")
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert is_valid, f"Errors: {errors}"

    def test_valid_all_themes_accepted(self, temp_dir):
        for theme in VALID_THEMES:
            pkg_dir = temp_dir / f"prism-{theme}"
            pkg_dir.mkdir()
            (pkg_dir / "package.yaml").write_text(
                yaml.dump(
                    {
                        "package": {"name": f"prism-{theme}", "version": "1.0.0", "description": "Test"},
                        "prism_config": {"theme": theme},
                    }
                )
            )
            validator = PrismValidator()
            is_valid, errors, warnings = validator.validate_package(pkg_dir)
            theme_warnings = [w for w in warnings if "theme" in w.lower()]
            assert len(theme_warnings) == 0, f"Theme {theme} should be valid"

    def test_valid_all_field_types_accepted(self, temp_dir):
        pkg_dir = temp_dir / "fields-prism"
        pkg_dir.mkdir()
        fields = [{"id": f"field_{t}", "label": f"Field {t}", "type": t} for t in VALID_FIELD_TYPES]
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "fields-prism", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": fields,
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        type_errors = [e for e in errors if "type" in e.lower()]
        assert len(type_errors) == 0

    def test_valid_prism_with_metadata(self, temp_dir):
        pkg_dir = temp_dir / "meta-prism"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "meta-prism", "version": "1.0.0", "description": "Test"},
                    "metadata": {"tags": ["company", "template"], "company_size": "medium"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert is_valid, f"Errors: {errors}"

    def test_readme_present_suppresses_warning(self, temp_dir):
        pkg_dir = temp_dir / "with-readme"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "with-readme", "version": "1.0.0", "description": "Test"},
                }
            )
        )
        (pkg_dir / "README.md").write_text("# Readme\n")
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        readme_warnings = [w for w in warnings if "README" in w]
        assert len(readme_warnings) == 0


@pytest.mark.unit
class TestPrismValidatorErrors:
    """Tests for invalid prism structures that should produce errors."""

    def test_nonexistent_directory(self, temp_dir):
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(temp_dir / "does_not_exist")
        assert not is_valid
        assert any("does not exist" in e for e in errors)

    def test_path_not_a_directory(self, temp_dir):
        file_path = temp_dir / "notadir.yaml"
        file_path.write_text("key: value")
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(file_path)
        assert not is_valid
        assert any("not a directory" in e for e in errors)

    def test_missing_package_yaml(self, temp_dir):
        pkg_dir = temp_dir / "empty-prism"
        pkg_dir.mkdir()
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("package.yaml" in e for e in errors)

    def test_empty_package_yaml(self, temp_dir):
        pkg_dir = temp_dir / "empty-yaml"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text("")
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid

    def test_invalid_yaml_syntax(self, temp_dir):
        pkg_dir = temp_dir / "bad-yaml"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text("invalid: yaml: [[[")
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("YAML" in e or "yaml" in e.lower() for e in errors)

    def test_missing_package_section(self, temp_dir):
        pkg_dir = temp_dir / "no-package"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(yaml.dump({"other_key": "value"}))
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("package" in e for e in errors)

    def test_missing_required_field_name(self, temp_dir):
        pkg_dir = temp_dir / "no-name"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(yaml.dump({"package": {"version": "1.0.0", "description": "No name"}}))
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("name" in e for e in errors)

    def test_missing_required_field_version(self, temp_dir):
        pkg_dir = temp_dir / "no-version"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump({"package": {"name": "no-version", "description": "No version"}})
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("version" in e for e in errors)

    def test_missing_required_field_description(self, temp_dir):
        pkg_dir = temp_dir / "no-desc"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(yaml.dump({"package": {"name": "no-desc", "version": "1.0.0"}}))
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("description" in e for e in errors)

    def test_empty_required_field(self, temp_dir):
        pkg_dir = temp_dir / "empty-name"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump({"package": {"name": "", "version": "1.0.0", "description": "Test"}})
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("name" in e for e in errors)

    def test_metadata_tags_must_be_list(self, temp_dir):
        pkg_dir = temp_dir / "bad-tags"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "bad-tags", "version": "1.0.0", "description": "Test"},
                    "metadata": {"tags": "should-be-a-list"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("tags" in e for e in errors)


@pytest.mark.unit
class TestBundledPrismsValidation:
    """Tests for bundled_prisms section validation."""

    def test_missing_config_file_is_error(self, temp_dir):
        pkg_dir = temp_dir / "missing-config"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "missing-config", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "base", "name": "Base", "required": True, "config": "base/nonexistent.yaml"}]
                    },
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("base/nonexistent.yaml" in e for e in errors)

    def test_present_config_file_is_valid(self, prism_dir):
        """prism_dir fixture has all config files — should be valid."""
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(prism_dir)
        assert is_valid
        config_errors = [e for e in errors if ".yaml" in e and "not found" in e]
        assert len(config_errors) == 0

    def test_missing_id_in_sub_prism(self, temp_dir):
        pkg_dir = temp_dir / "no-id"
        pkg_dir.mkdir()
        (pkg_dir / "base").mkdir()
        (pkg_dir / "base" / "base.yaml").write_text("key: value")
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "no-id", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {"base": [{"name": "No ID", "config": "base/base.yaml"}]},  # missing id
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("id" in e for e in errors)

    def test_missing_config_in_sub_prism_entry(self, temp_dir):
        pkg_dir = temp_dir / "no-config-key"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "no-config-key", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {"base": [{"id": "base", "name": "Base"}]},  # missing config key
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("config" in e for e in errors)

    def test_tier_must_be_list(self, temp_dir):
        pkg_dir = temp_dir / "dict-tier"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "dict-tier", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {"base": {"id": "base", "config": "base/base.yaml"}},  # dict not list
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("list" in e for e in errors)


@pytest.mark.unit
class TestPrismConfigValidation:
    """Tests for prism_config section validation."""

    def test_unknown_theme_produces_warning(self, temp_dir):
        pkg_dir = temp_dir / "bad-theme"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "bad-theme", "version": "1.0.0", "description": "Test"},
                    "prism_config": {"theme": "ultraviolet"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        # Unknown theme is a warning, not an error
        assert any("ultraviolet" in w for w in warnings)

    def test_unknown_theme_does_not_fail_validation(self, temp_dir):
        pkg_dir = temp_dir / "warn-theme"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "warn-theme", "version": "1.0.0", "description": "Test"},
                    "prism_config": {"theme": "invalid_theme"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        # Only a warning, not a fatal error
        assert is_valid

    def test_sources_must_be_list(self, temp_dir):
        pkg_dir = temp_dir / "bad-sources"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "bad-sources", "version": "1.0.0", "description": "Test"},
                    "prism_config": {"sources": "not-a-list"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("sources" in e for e in errors)


@pytest.mark.unit
class TestUserInfoFieldsValidation:
    """Tests for user_info_fields validation."""

    def test_valid_text_field(self, temp_dir):
        pkg_dir = temp_dir / "text-field"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "text-field", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": [{"id": "name", "label": "Name", "type": "text"}],
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert is_valid

    def test_invalid_field_type_produces_warning(self, temp_dir):
        pkg_dir = temp_dir / "bad-type"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "bad-type", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": [{"id": "x", "label": "X", "type": "color"}],
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert any("color" in w for w in warnings)

    def test_missing_field_id_is_error(self, temp_dir):
        pkg_dir = temp_dir / "missing-id"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "missing-id", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": [{"label": "Name", "type": "text"}],  # missing id
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("id" in e for e in errors)

    def test_missing_field_label_is_error(self, temp_dir):
        pkg_dir = temp_dir / "missing-label"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "missing-label", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": [{"id": "name", "type": "text"}],  # missing label
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("label" in e for e in errors)

    def test_missing_field_type_is_error(self, temp_dir):
        pkg_dir = temp_dir / "missing-type"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "missing-type", "version": "1.0.0", "description": "Test"},
                    "user_info_fields": [{"id": "name", "label": "Name"}],  # missing type
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        assert not is_valid
        assert any("type" in e for e in errors)

    def test_no_user_fields_produces_warning(self, temp_dir):
        pkg_dir = temp_dir / "no-fields"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "no-fields", "version": "1.0.0", "description": "Test"},
                }
            )
        )
        validator = PrismValidator()
        is_valid, errors, warnings = validator.validate_package(pkg_dir)
        # No fields is a warning, not an error
        assert is_valid
        assert any("user_info_fields" in w for w in warnings)


@pytest.mark.unit
class TestGetPackageInfo:
    """Tests for PrismValidator.get_package_info()."""

    def test_returns_info_for_valid_prism(self, prism_dir):
        validator = PrismValidator()
        info = validator.get_package_info(prism_dir)
        assert info["name"] == "test-prism"
        assert info["version"] == "1.0.0"
        assert not info["error"]

    def test_error_flag_for_missing_package_yaml(self, temp_dir):
        pkg_dir = temp_dir / "no-yaml"
        pkg_dir.mkdir()
        validator = PrismValidator()
        info = validator.get_package_info(pkg_dir)
        assert info["error"] is True

    def test_has_bundled_prisms_flag(self, prism_dir):
        validator = PrismValidator()
        info = validator.get_package_info(prism_dir)
        assert info["has_bundled_prisms"] is True

    def test_theme_extracted_from_prism_config(self, prism_dir):
        validator = PrismValidator()
        info = validator.get_package_info(prism_dir)
        assert info["theme"] == "ocean"


@pytest.mark.unit
class TestValidateAllPackages:
    """Tests for validate_all_packages() bulk validation."""

    def test_validates_multiple_valid_packages(self, temp_dir):
        for i in range(3):
            pkg_dir = temp_dir / f"prism-{i}"
            pkg_dir.mkdir()
            (pkg_dir / "package.yaml").write_text(
                yaml.dump(
                    {
                        "package": {"name": f"prism-{i}", "version": "1.0.0", "description": f"Test {i}"},
                    }
                )
            )

        valid, invalid = validate_all_packages(temp_dir)
        assert len(valid) == 3
        assert len(invalid) == 0

    def test_separates_valid_and_invalid(self, temp_dir):
        # Valid
        good_dir = temp_dir / "good-prism"
        good_dir.mkdir()
        (good_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "good-prism", "version": "1.0.0", "description": "Good"},
                }
            )
        )

        # Invalid — bad YAML
        bad_dir = temp_dir / "bad-prism"
        bad_dir.mkdir()
        (bad_dir / "package.yaml").write_text("invalid: yaml: [[[")

        valid, invalid = validate_all_packages(temp_dir)
        assert len(valid) == 1
        assert len(invalid) == 1
        assert valid[0]["name"] == "good-prism"

    def test_empty_directory_returns_empty_lists(self, temp_dir):
        valid, invalid = validate_all_packages(temp_dir)
        assert valid == []
        assert invalid == []

    def test_nonexistent_directory_returns_empty_lists(self, temp_dir):
        valid, invalid = validate_all_packages(temp_dir / "nonexistent")
        assert valid == []
        assert invalid == []

    def test_skips_hidden_directories(self, temp_dir):
        hidden = temp_dir / ".hidden"
        hidden.mkdir()
        (hidden / "package.yaml").write_text(
            yaml.dump({"package": {"name": "hidden", "version": "1.0.0", "description": "Hidden"}})
        )
        valid, invalid = validate_all_packages(temp_dir)
        assert len(valid) == 0  # hidden dirs skipped

    def test_result_includes_errors_and_warnings(self, temp_dir):
        bad_dir = temp_dir / "broken"
        bad_dir.mkdir()
        (bad_dir / "package.yaml").write_text(
            yaml.dump({"package": {"version": "1.0.0", "description": "Missing name"}})
        )
        valid, invalid = validate_all_packages(temp_dir)
        assert len(invalid) == 1
        assert "errors" in invalid[0]
        assert len(invalid[0]["errors"]) > 0

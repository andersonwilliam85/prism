"""Unit tests for ValidationEngine."""

from __future__ import annotations

from prism.engines.validation_engine.validation_engine import ValidationEngine
from prism.engines.validation_engine.i_validation_engine import IValidationEngine


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(ValidationEngine(), IValidationEngine)


class TestValidate:
    def test_valid_config(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "test", "version": "1.0", "description": "A test"},
            "bundled_prisms": {"base": [{"id": "base", "config": "base.yaml"}]},
            "user_info_fields": [{"id": "name", "label": "Name", "type": "text"}],
        }
        valid, errors, warnings = engine.validate(config)
        assert valid is True
        assert errors == []

    def test_empty_config(self):
        engine = ValidationEngine()
        valid, errors, _ = engine.validate({})
        assert valid is False
        assert "Config is empty" in errors[0]

    def test_missing_package(self):
        engine = ValidationEngine()
        valid, errors, _ = engine.validate({"bundled_prisms": {}})
        assert valid is False
        assert any("package" in e for e in errors)

    def test_missing_required_fields(self):
        engine = ValidationEngine()
        config = {"package": {"name": "test"}}
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("version" in e for e in errors)

    def test_empty_required_field(self):
        engine = ValidationEngine()
        config = {"package": {"name": "", "version": "1.0", "description": "x"}}
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("Empty" in e for e in errors)

    def test_no_bundled_prisms_warning(self):
        engine = ValidationEngine()
        config = {"package": {"name": "x", "version": "1", "description": "x"}}
        valid, _, warnings = engine.validate(config)
        assert valid is True
        assert any("bundled_prisms" in w for w in warnings)

    def test_theme_must_be_string(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "prism_config": {"theme": 123},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("theme" in e for e in errors)

    def test_custom_theme_allowed(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "prism_config": {"theme": "custom-corporate-blue"},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is True

    def test_bundled_prisms_validation(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "bundled_prisms": {"base": [{"no_id": True}]},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("id" in e for e in errors)

    def test_user_info_fields_validation(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "user_info_fields": [{"id": "x", "label": "X", "type": "invalid_type"}],
        }
        _, _, warnings = engine.validate(config)
        assert any("unknown type" in w for w in warnings)

    def test_metadata_tags_must_be_list(self):
        engine = ValidationEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "metadata": {"tags": "not-a-list"},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("tags" in e for e in errors)

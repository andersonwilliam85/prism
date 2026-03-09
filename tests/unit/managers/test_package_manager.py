"""Unit tests for PackageManager.

BDT: Manager tier — real engine, mocked accessor.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prism.engines.validation_engine.validation_engine import ValidationEngine
from prism.managers.package_manager.package_manager import PackageManager
from prism.models.package_info import UserField


@pytest.fixture
def file_accessor():
    return MagicMock()


@pytest.fixture
def validation_engine():
    return ValidationEngine()


@pytest.fixture
def prisms_dir():
    return Path("/fake/prisms")


@pytest.fixture
def manager(validation_engine, file_accessor, prisms_dir):
    return PackageManager(
        validation_engine=validation_engine,
        file_accessor=file_accessor,
        prisms_dir=prisms_dir,
    )


# ------------------------------------------------------------------
# list_packages
# ------------------------------------------------------------------


class TestListPackages:
    def test_returns_package_info_objects(self, manager, file_accessor):
        file_accessor.list_packages.return_value = [
            {
                "name": "startup",
                "version": "1.0.0",
                "description": "Startup prism",
                "type": "prism",
                "path": "/fake/prisms/startup",
            }
        ]
        result = manager.list_packages()
        assert len(result) == 1
        assert result[0].name == "startup"
        assert result[0].version == "1.0.0"

    def test_returns_empty_when_no_packages(self, manager, file_accessor):
        file_accessor.list_packages.return_value = []
        assert manager.list_packages() == []


# ------------------------------------------------------------------
# get_info
# ------------------------------------------------------------------


class TestGetInfo:
    def test_returns_package_info(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "package": {"name": "acme", "version": "2.0.0", "description": "Acme Corp", "type": "enterprise"},
            "bundled_prisms": {"roles": [{"id": "dev"}]},
            "tools_required": ["git", "node"],
        }
        file_accessor.find_package.return_value = Path("/fake/prisms/acme")

        info = manager.get_info("acme")
        assert info.name == "acme"
        assert info.has_tiers is True
        assert info.has_tools is True

    def test_no_tiers_no_tools(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {"package": {"name": "minimal"}}
        file_accessor.find_package.return_value = Path("/fake/prisms/minimal")

        info = manager.get_info("minimal")
        assert info.has_tiers is False
        assert info.has_tools is False


# ------------------------------------------------------------------
# get_tiers
# ------------------------------------------------------------------


class TestGetTiers:
    def test_parses_bundled_prisms(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "bundled_prisms": {
                "roles": [
                    {"id": "frontend", "name": "Frontend Developer", "required": False},
                    {"id": "base", "name": "Base Config", "required": True},
                ],
            }
        }
        tiers = manager.get_tiers("startup")
        assert "roles" in tiers
        assert len(tiers["roles"]) == 2
        assert tiers["roles"][1].required is True

    def test_empty_when_no_bundled(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {}
        assert manager.get_tiers("minimal") == {}


# ------------------------------------------------------------------
# validate
# ------------------------------------------------------------------


class TestValidate:
    def test_valid_package(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "package": {"name": "test", "version": "1.0.0", "description": "Test"}
        }
        valid, errors, warnings = manager.validate("test")
        assert valid is True
        assert errors == []

    def test_invalid_package(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {"package": {}}
        valid, errors, warnings = manager.validate("bad")
        assert valid is False
        assert len(errors) > 0


# ------------------------------------------------------------------
# validate_all
# ------------------------------------------------------------------


class TestValidateAll:
    def test_validates_all_packages(self, manager, file_accessor):
        file_accessor.list_packages.return_value = [
            {"name": "a", "version": "1.0", "description": "A", "type": "prism", "path": "/fake/a"},
            {"name": "b", "version": "1.0", "description": "B", "type": "prism", "path": "/fake/b"},
        ]
        file_accessor.get_package_config.side_effect = [
            {"package": {"name": "a", "version": "1.0", "description": "A"}},
            {"package": {"name": "b", "version": "1.0", "description": "B"}},
        ]
        file_accessor.find_package.return_value = Path("/fake/prisms/x")

        results = manager.validate_all()
        assert "a" in results
        assert "b" in results
        assert results["a"][0] is True
        assert results["b"][0] is True


# ------------------------------------------------------------------
# get_user_fields
# ------------------------------------------------------------------


class TestGetUserFields:
    def test_parses_user_fields(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "user_info_fields": [
                {"id": "name", "label": "Full Name", "type": "text", "required": True},
                {"id": "role", "label": "Role", "type": "select", "options": ["dev", "qa"]},
            ]
        }
        fields = manager.get_user_fields("test")
        assert len(fields) == 2
        assert fields[0].id == "name"
        assert fields[0].required is True
        assert fields[1].type == "select"

    def test_empty_when_no_fields(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {}
        assert manager.get_user_fields("test") == []

    def test_skips_invalid_entries(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "user_info_fields": [
                {"id": "name", "label": "Name"},
                "not-a-dict",
                {"label": "No ID"},  # missing id
            ]
        }
        fields = manager.get_user_fields("test")
        assert len(fields) == 1


# ------------------------------------------------------------------
# get_user_defaults
# ------------------------------------------------------------------


class TestGetUserDefaults:
    def test_returns_placeholders_as_defaults(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "user_info_fields": [
                {"id": "name", "label": "Name", "placeholder": "Jane Doe"},
                {"id": "email", "label": "Email"},
            ]
        }
        defaults = manager.get_user_defaults("test")
        assert defaults == {"name": "Jane Doe"}


# ------------------------------------------------------------------
# validate_user_input
# ------------------------------------------------------------------


class TestValidateUserInput:
    def test_valid_input(self, manager):
        fields = [
            UserField(id="name", label="Name", required=True),
            UserField(id="email", label="Email", type="email"),
        ]
        valid, errors = manager.validate_user_input({"name": "Alice", "email": "alice@test.com"}, fields)
        assert valid is True
        assert errors == []

    def test_missing_required(self, manager):
        fields = [UserField(id="name", label="Name", required=True)]
        valid, errors = manager.validate_user_input({}, fields)
        assert valid is False
        assert "Required field missing: Name" in errors

    def test_invalid_email(self, manager):
        fields = [UserField(id="email", label="Email", type="email")]
        valid, errors = manager.validate_user_input({"email": "not-an-email"}, fields)
        assert valid is False

    def test_invalid_select(self, manager):
        fields = [UserField(id="role", label="Role", type="select", options=["dev", "qa"])]
        valid, errors = manager.validate_user_input({"role": "ceo"}, fields)
        assert valid is False

"""Unit tests for packages API blueprint.

BDT: API tier — real managers + mocked accessors via Container.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prism.ui.app import create_app


@pytest.fixture
def mock_file_accessor():
    mock = MagicMock()
    mock.list_packages.return_value = [
        {"name": "startup", "description": "Startup Prism", "version": "1.0.0", "path": "/fake/prisms/startup"},
        {"name": "acme-corp", "description": "Acme Corp", "version": "2.0.0", "path": "/fake/prisms/acme-corp"},
    ]
    mock.find_package.return_value = Path("/fake/prisms/startup")
    return mock


@pytest.fixture
def valid_config():
    return {
        "package": {"name": "startup", "version": "1.0.0", "description": "Startup Prism"},
        "prism_config": {"theme": "ocean"},
        "bundled_prisms": {
            "team": [
                {"id": "frontend", "name": "Frontend", "config": "configs/frontend.yaml", "required": False},
                {"id": "backend", "name": "Backend", "config": "configs/backend.yaml", "required": True},
            ]
        },
        "user_info_fields": [
            {"id": "name", "label": "Full Name", "type": "text", "required": True, "placeholder": "Jane"},
            {"id": "role", "label": "Role", "type": "text", "required": False},
        ],
    }


@pytest.fixture
def app(mock_file_accessor, valid_config):
    mock_file_accessor.get_package_config.return_value = valid_config
    with patch("prism.container.FileAccessor", return_value=mock_file_accessor):
        with patch("prism.container.CommandAccessor"):
            with patch("prism.container.SystemAccessor"):
                with patch("prism.container.RegistryAccessor"):
                    application = create_app(prisms_dir=Path("/fake/prisms"))
                    application.config["TESTING"] = True
                    yield application


@pytest.fixture
def client(app):
    return app.test_client()


class TestListPackages:
    def test_returns_valid_packages(self, client):
        resp = client.get("/api/packages")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data["packages"]) >= 1
        assert "stats" in data

    def test_package_has_required_fields(self, client):
        resp = client.get("/api/packages")
        data = json.loads(resp.data)
        if data["packages"]:
            pkg = data["packages"][0]
            assert "id" in pkg
            assert "name" in pkg
            assert "displayName" in pkg
            assert "version" in pkg


class TestGetMetadata:
    def test_returns_metadata(self, client):
        resp = client.get("/api/package/startup/metadata")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert "has_tiers" in data
        assert "has_tools" in data
        assert "display_name" in data

    def test_detects_optional_tiers(self, client):
        resp = client.get("/api/package/startup/metadata")
        data = json.loads(resp.data)
        assert data["has_tiers"] is True
        assert data["has_optional_tiers"] is True


class TestGetTiers:
    def test_returns_optional_tiers(self, client):
        resp = client.get("/api/package/startup/tiers")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert "optional_tiers" in data
        # Only the non-required "frontend" should appear
        if data["optional_tiers"]:
            tier = data["optional_tiers"][0]
            assert "name" in tier
            assert "options" in tier
            option_ids = [o["id"] for o in tier["options"]]
            assert "frontend" in option_ids
            assert "backend" not in option_ids  # required items excluded


class TestGetUserFields:
    def test_returns_fields(self, client):
        resp = client.get("/api/package/startup/user-fields")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(data["fields"]) == 2
        assert data["fields"][0]["id"] == "name"

    def test_defaults_when_no_fields(self, client, app):
        container = app.config["container"]
        container.file_accessor.get_package_config.return_value = {
            "package": {"name": "minimal", "version": "1.0.0", "description": "Minimal"},
        }
        resp = client.get("/api/package/minimal/user-fields")
        data = json.loads(resp.data)
        assert len(data["fields"]) == 2
        assert data["fields"][0]["id"] == "name"
        assert data["fields"][1]["id"] == "email"


class TestGetConfig:
    def test_returns_prism_config(self, client):
        resp = client.get("/api/package/startup/config")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["prism_config"]["theme"] == "ocean"
        assert data["package_name"] == "startup"

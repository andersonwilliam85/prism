"""Unit tests for validation API blueprint.

BDT: API tier — real engines + mocked accessors.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prism.ui.app import create_app


@pytest.fixture
def mock_file_accessor():
    mock = MagicMock()
    mock.list_packages.return_value = []
    mock.find_package.return_value = Path("/fake/prisms/startup")
    return mock


@pytest.fixture
def app(mock_file_accessor):
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


class TestValidateConfigs:
    def test_valid_package(self, client, mock_file_accessor):
        mock_file_accessor.get_package_config.return_value = {
            "package": {"name": "test", "version": "1.0.0", "description": "Test"},
        }
        resp = client.get("/api/package/test/validate-configs")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["valid"] is True
        assert data["summary"]["total_errors"] == 0

    def test_invalid_package(self, client, mock_file_accessor):
        mock_file_accessor.get_package_config.return_value = {
            "package": {},  # Missing required fields
        }
        resp = client.get("/api/package/bad/validate-configs")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["valid"] is False
        assert data["summary"]["total_errors"] > 0

    def test_missing_package(self, client, mock_file_accessor):
        mock_file_accessor.get_package_config.side_effect = FileNotFoundError("not found")
        resp = client.get("/api/package/missing/validate-configs")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["valid"] is False

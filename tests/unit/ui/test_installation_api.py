"""Unit tests for installation API blueprint.

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
    mock.exists.return_value = False
    mock.find_package.return_value = Path("/fake/prisms/startup")
    mock.read_yaml.return_value = {}
    mock.list_packages.return_value = []
    return mock


@pytest.fixture
def mock_command_accessor():
    mock = MagicMock()
    mock.pkg_is_installed.return_value = True
    mock.ssh_key_exists.return_value = True
    return mock


@pytest.fixture
def mock_system_accessor():
    mock = MagicMock()
    mock.get_platform.return_value = ("mac", "Apple Silicon")
    mock.get_installed_version.return_value = "3.11"
    return mock


@pytest.fixture
def valid_config():
    return {
        "package": {"name": "startup", "version": "1.0.0", "description": "Startup Prism"},
        "prism_config": {"theme": "ocean"},
        "bundled_prisms": {},
    }


@pytest.fixture
def app(mock_file_accessor, mock_command_accessor, mock_system_accessor, valid_config):
    mock_file_accessor.get_package_config.return_value = valid_config
    with patch("prism.container.FileAccessor", return_value=mock_file_accessor):
        with patch("prism.container.CommandAccessor", return_value=mock_command_accessor):
            with patch("prism.container.SystemAccessor", return_value=mock_system_accessor):
                with patch("prism.container.RegistryAccessor"):
                    application = create_app(prisms_dir=Path("/fake/prisms"))
                    application.config["TESTING"] = True
                    yield application


@pytest.fixture
def client(app):
    return app.test_client()


class TestInstallEndpoint:
    def test_rejects_empty_prism_id(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps({"package": ""}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data["success"] is False

    def test_rejects_missing_package(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert data["success"] is False

    def test_successful_install(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "startup",
                    "userInfo": {"name": "Alice", "email": "alice@test.com"},
                }
            ),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True
        assert "progress" in data

    def test_install_with_sub_prisms(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "startup",
                    "userInfo": {"name": "Bob"},
                    "selectedSubPrisms": {"team": "frontend"},
                }
            ),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True

    def test_install_with_tools_excluded(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "startup",
                    "userInfo": {},
                    "toolsExcluded": ["docker"],
                }
            ),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True

    def test_install_returns_progress_log(self, client):
        resp = client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "startup",
                    "userInfo": {"name": "Carol"},
                }
            ),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert isinstance(data.get("progress"), list)
        if data["progress"]:
            entry = data["progress"][0]
            assert "step" in entry
            assert "message" in entry
            assert "level" in entry

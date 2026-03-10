"""Unit tests for installation API blueprint.

BDT: API tier — real managers + mocked accessors via Container.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prism.ui.api import installation as installation_module
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
def mock_sudo_accessor():
    mock = MagicMock()
    mock.validate_password.return_value = True
    mock.is_sudo_available.return_value = True
    return mock


@pytest.fixture
def app(mock_file_accessor, mock_command_accessor, mock_system_accessor, mock_sudo_accessor, valid_config):
    mock_file_accessor.get_package_config.return_value = valid_config
    with patch("prism.container.FileAccessor", return_value=mock_file_accessor):
        with patch("prism.container.CommandAccessor", return_value=mock_command_accessor):
            with patch("prism.container.SystemAccessor", return_value=mock_system_accessor):
                with patch("prism.container.RegistryAccessor"):
                    with patch("prism.container.SudoAccessor", return_value=mock_sudo_accessor):
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


class TestSudoValidation:
    """Tests for sudo validation and session management endpoints."""

    @pytest.fixture(autouse=True)
    def _clear_sessions(self):
        """Clear the in-memory session store between tests."""
        installation_module._sudo_sessions.clear()
        yield
        installation_module._sudo_sessions.clear()

    def test_validate_sudo_success(self, client, mock_sudo_accessor):
        mock_sudo_accessor.validate_password.return_value = True
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "correct"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True
        assert "token" in data

    def test_validate_sudo_wrong_password(self, client, mock_sudo_accessor):
        mock_sudo_accessor.validate_password.return_value = False
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "wrong"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 401
        assert data["success"] is False
        assert "remaining_attempts" in data

    def test_validate_sudo_empty_password(self, client):
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_validate_sudo_lockout(self, client, mock_sudo_accessor):
        mock_sudo_accessor.validate_password.return_value = False
        # First attempt — get the token
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "wrong"}),
            content_type="application/json",
        )
        token = json.loads(resp.data)["token"]
        # Subsequent attempts with same token
        for _ in range(2):
            resp = client.post(
                "/api/installation/validate-sudo",
                data=json.dumps({"password": "wrong", "token": token}),
                content_type="application/json",
            )
        data = json.loads(resp.data)
        assert resp.status_code == 429
        assert data.get("locked") is True

    def test_session_status_valid(self, client, mock_sudo_accessor):
        mock_sudo_accessor.validate_password.return_value = True
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "correct"}),
            content_type="application/json",
        )
        token = json.loads(resp.data)["token"]

        resp = client.get(f"/api/installation/sudo-session/{token}")
        data = json.loads(resp.data)
        assert data["valid"] is True
        assert data["expired"] is False

    def test_session_status_not_found(self, client):
        resp = client.get("/api/installation/sudo-session/nonexistent")
        assert resp.status_code == 404

    def test_sudo_not_available(self, client, mock_sudo_accessor):
        mock_sudo_accessor.is_sudo_available.return_value = False
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "test"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 400
        assert "not available" in data["error"]

    def test_retry_with_token(self, client, mock_sudo_accessor):
        mock_sudo_accessor.validate_password.return_value = False
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "wrong"}),
            content_type="application/json",
        )
        token = json.loads(resp.data)["token"]

        mock_sudo_accessor.validate_password.return_value = True
        resp = client.post(
            "/api/installation/validate-sudo",
            data=json.dumps({"password": "correct", "token": token}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["token"] == token

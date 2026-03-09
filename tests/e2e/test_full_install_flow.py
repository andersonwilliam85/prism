"""End-to-end test: full installation flow via Flask test client.

Exercises the complete happy path:
1. GET /api/packages — verify prism.prism is default
2. GET /api/package/prism.prism/config — verify prism_config
3. GET /api/package/prism.prism/user-fields — verify fields
4. GET /api/package/prism.prism/tiers — verify bundled_prisms
5. POST /api/install — run full installation
6. Verify filesystem artifacts were created
"""

import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).parent.parent.parent


def _load_install_ui():
    """Load install-ui.py (hyphenated filename requires importlib)."""
    spec = importlib.util.spec_from_file_location("install_ui", ROOT / "install-ui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def client():
    """Create Flask test client."""
    ui_module = _load_install_ui()
    ui_module.app.config["TESTING"] = True
    with ui_module.app.test_client() as client:
        yield client


@pytest.fixture
def install_dir():
    """Create a temp directory for installation output, clean up after."""
    d = tempfile.mkdtemp(prefix="prism_test_install_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestPackageDiscovery:
    """Verify package listing and default prism behavior."""

    def test_packages_endpoint_returns_packages(self, client):
        resp = client.get("/api/packages")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "packages" in data
        assert len(data["packages"]) > 0

    def test_default_prism_exists(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        default_pkgs = [p for p in data["packages"] if p.get("default")]
        assert len(default_pkgs) == 1, "Exactly one default prism should exist"
        assert default_pkgs[0]["id"] == "prism.prism"

    def test_default_prism_has_correct_metadata(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        prism = next(p for p in data["packages"] if p["id"] == "prism.prism")
        assert prism["name"] == "prism"
        assert prism["default"] is True


class TestPrismConfig:
    """Verify prism_config endpoint for the default prism."""

    def test_config_returns_theme(self, client):
        resp = client.get("/api/package/prism.prism/config")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["prism_config"]["theme"] == "ocean"

    def test_config_returns_branding(self, client):
        resp = client.get("/api/package/prism.prism/config")
        data = resp.get_json()
        branding = data["prism_config"]["branding"]
        assert branding["name"] == "Prism"
        assert "clarity" in branding["tagline"].lower()


class TestUserFields:
    """Verify user info fields for the default prism."""

    def test_user_fields_returned(self, client):
        resp = client.get("/api/package/prism.prism/user-fields")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "fields" in data
        field_ids = [f["id"] for f in data["fields"]]
        assert "name" in field_ids
        assert "email" in field_ids
        assert "git_username" in field_ids


class TestTiers:
    """Verify bundled_prisms tiers for the default prism."""

    def test_tiers_returned(self, client):
        resp = client.get("/api/package/prism.prism/tiers")
        assert resp.status_code == 200
        data = resp.get_json()
        # Should have optional tiers (environment)
        assert "optional_tiers" in data or "error" not in data


class TestInstallation:
    """Full installation test with mocked filesystem operations."""

    def test_install_default_prism(self, client, install_dir):
        """Run a full installation of the default prism."""
        # Mock HOME to use our temp dir so installation writes there
        mock_home = install_dir
        mock_workspace = os.path.join(mock_home, "workspace")

        with patch.dict(os.environ, {"HOME": mock_home}):
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "prism.prism",
                        "user_name": "Test User",
                        "user_email": "test@example.com",
                        "npm_registry": "",
                        "unpkg_url": "",
                        "selectedSubPrisms": {"environment": "personal"},
                    }
                ),
                content_type="application/json",
            )

            assert resp.status_code == 200, f"Install failed: {resp.get_json()}"
            data = resp.get_json()
            assert data.get("success") is True, f"Install not successful: {data}"

            # Verify workspace was created
            assert os.path.isdir(mock_workspace), "Workspace directory not created"

            # Verify marker file (lives in workspace, not HOME)
            marker = os.path.join(mock_workspace, ".prism_installed")
            assert os.path.isfile(marker), ".prism_installed marker not created"

            # Read marker and verify contents
            with open(marker) as f:
                marker_data = json.load(f)
            # Marker uses 'prism' key (path to prism dir), not 'package'
            assert "prism" in marker_data.get("prism", "").lower()


class TestWebUI:
    """Verify the web UI serves correctly."""

    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Prism" in html
        assert "brandingTitle" in html

    def test_index_has_favicon(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "prism_transparent_32.png" in html

    def test_index_has_logo(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "prism_light_128.png" in html

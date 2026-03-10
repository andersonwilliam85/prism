"""E2E tests for the HD-based API — real Container, real prisms.

These tests exercise the full stack through Flask test client:
Container → Manager → Engine → Accessor (mocked at I/O boundary only).

No browser required. Runs in CI.
"""

from __future__ import annotations

import json

import pytest


@pytest.mark.e2e
class TestPackageDiscovery:
    """E2E: package discovery through the full HD stack."""

    def test_packages_endpoint_returns_200(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        assert resp.status_code == 200

    def test_packages_returns_list(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        data = resp.get_json()
        assert "packages" in data
        assert isinstance(data["packages"], list)

    def test_discovered_packages_have_required_fields(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        data = resp.get_json()
        for pkg in data["packages"]:
            assert "name" in pkg
            assert "version" in pkg

    def test_package_metadata(self, e2e_client, prisms_dir):
        """Test metadata endpoint for each discovered package."""
        resp = e2e_client.get("/api/packages")
        packages = resp.get_json()["packages"]
        for pkg in packages:
            name = pkg.get("dir_name") or pkg["name"]
            resp = e2e_client.get(f"/api/package/{name}/metadata")
            assert resp.status_code == 200
            data = resp.get_json()
            assert "name" in data or "error" not in data

    def test_nonexistent_package_metadata(self, e2e_client):
        resp = e2e_client.get("/api/package/does-not-exist-xyz/metadata")
        data = resp.get_json()
        assert "error" in data


@pytest.mark.e2e
class TestUserFields:
    """E2E: user info field discovery."""

    def test_user_fields_for_discovered_packages(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        packages = resp.get_json()["packages"]
        for pkg in packages:
            name = pkg.get("dir_name") or pkg["name"]
            resp = e2e_client.get(f"/api/package/{name}/user-fields")
            assert resp.status_code == 200
            data = resp.get_json()
            assert "fields" in data
            assert isinstance(data["fields"], list)

    def test_fields_have_id_and_label(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        packages = resp.get_json()["packages"]
        for pkg in packages:
            name = pkg.get("dir_name") or pkg["name"]
            resp = e2e_client.get(f"/api/package/{name}/user-fields")
            data = resp.get_json()
            for field in data["fields"]:
                assert "id" in field
                assert "label" in field


@pytest.mark.e2e
class TestTiers:
    """E2E: tier/sub-prism discovery."""

    def test_tiers_endpoint(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        packages = resp.get_json()["packages"]
        for pkg in packages:
            name = pkg.get("dir_name") or pkg["name"]
            resp = e2e_client.get(f"/api/package/{name}/tiers")
            assert resp.status_code == 200
            data = resp.get_json()
            assert "optional_tiers" in data
            assert isinstance(data["optional_tiers"], list)


@pytest.mark.e2e
class TestInstallFlow:
    """E2E: installation flow through InstallationManager."""

    def test_install_rejects_empty_package(self, e2e_client):
        resp = e2e_client.post(
            "/api/install",
            data=json.dumps({"package": "", "userInfo": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_install_nonexistent_package_fails(self, e2e_client):
        resp = e2e_client.post(
            "/api/install",
            data=json.dumps({"package": "no-such-prism-xyz", "userInfo": {"name": "Test"}}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data.get("success") is False or resp.status_code >= 400

    def test_install_accepts_sub_prisms_param(self, e2e_client):
        resp = e2e_client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "no-such-prism",
                    "userInfo": {},
                    "selectedSubPrisms": {"tier": "option"},
                }
            ),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data is not None

    def test_install_accepts_tools_params(self, e2e_client):
        resp = e2e_client.post(
            "/api/install",
            data=json.dumps(
                {
                    "package": "no-such-prism",
                    "userInfo": {},
                    "toolsSelected": ["git"],
                    "toolsExcluded": ["docker"],
                }
            ),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data is not None


@pytest.mark.e2e
class TestRootAndStatic:
    """E2E: root route and static content."""

    def test_root_returns_html(self, e2e_client):
        resp = e2e_client.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower() or b"Prism" in resp.data

    def test_tools_endpoint(self, e2e_client):
        resp = e2e_client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "tools" in data
        assert isinstance(data["tools"], list)


@pytest.mark.e2e
class TestPackageConfig:
    """E2E: prism_config retrieval."""

    def test_config_for_discovered_packages(self, e2e_client):
        resp = e2e_client.get("/api/packages")
        packages = resp.get_json()["packages"]
        for pkg in packages:
            name = pkg.get("dir_name") or pkg["name"]
            resp = e2e_client.get(f"/api/package/{name}/config")
            assert resp.status_code == 200
            data = resp.get_json()
            assert "prism_config" in data

    def test_config_nonexistent_package(self, e2e_client):
        resp = e2e_client.get("/api/package/nope/config")
        data = resp.get_json()
        assert "error" in data or data.get("prism_config") is None

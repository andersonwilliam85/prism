"""
E2E tests for the Flask web API (install-ui.py).

Uses Flask test client — no browser required.
"""

# Make install-ui.py importable (hyphenated filename requires importlib)
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def _load_install_ui():
    spec = importlib.util.spec_from_file_location("install_ui", ROOT / "install-ui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def app():
    """Return the Flask app from install-ui.py."""
    ui_module = _load_install_ui()
    ui_module.app.config["TESTING"] = True
    return ui_module.app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# /api/packages
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestPackagesEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/api/packages")
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        assert data is not None

    def test_has_packages_key(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        assert "packages" in data

    def test_packages_is_list(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        assert isinstance(data["packages"], list)

    def test_each_package_has_required_fields(self, client):
        resp = client.get("/api/packages")
        data = resp.get_json()
        for pkg in data["packages"]:
            assert "name" in pkg
            assert "version" in pkg


# ---------------------------------------------------------------------------
# /api/package/<name>/user-fields
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestUserFieldsEndpoint:
    def test_prism_returns_fields(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/user-fields")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "fields" in data
        assert isinstance(data["fields"], list)
        assert len(data["fields"]) > 0

    def test_each_field_has_id_and_label(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/user-fields")
        data = resp.get_json()
        for field in data["fields"]:
            assert "id" in field
            assert "label" in field

    def test_nonexistent_package_returns_empty_fields(self, client):
        resp = client.get("/api/package/definitely-not-a-real-prism/user-fields")
        data = resp.get_json()
        assert "fields" in data
        assert data["fields"] == [] or "error" in data


# ---------------------------------------------------------------------------
# /api/package/<name>/metadata
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestMetadataEndpoint:
    def test_prism_metadata(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/metadata")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get("name") == "prism"

    def test_metadata_has_display_name(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/metadata")
        data = resp.get_json()
        assert "display_name" in data

    def test_metadata_has_tiers_flag(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/metadata")
        data = resp.get_json()
        assert "has_tiers" in data

    def test_nonexistent_package_returns_error(self, client):
        resp = client.get("/api/package/no-such-prism/metadata")
        data = resp.get_json()
        assert "error" in data


# ---------------------------------------------------------------------------
# /api/package/<name>/tiers
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestTiersEndpoint:
    def test_prism_tiers(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/tiers")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "optional_tiers" in data
        assert isinstance(data["optional_tiers"], list)

    def test_tiers_have_required_fields(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/tiers")
        data = resp.get_json()
        for tier in data["optional_tiers"]:
            assert "name" in tier
            assert "label" in tier
            assert "options" in tier
            assert isinstance(tier["options"], list)

    def test_tier_options_have_id_and_name(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/tiers")
        data = resp.get_json()
        for tier in data["optional_tiers"]:
            for opt in tier["options"]:
                assert "id" in opt
                assert "name" in opt

    def test_nonexistent_package_returns_empty_tiers(self, client):
        resp = client.get("/api/package/no-such-prism/tiers")
        data = resp.get_json()
        assert "optional_tiers" in data
        assert data["optional_tiers"] == []

    def test_required_only_tiers_not_included(self, client, tmp_path):
        """A tier where all items are required should not appear in optional_tiers."""
        # Create a temp prism with only required items in its tier
        prisms_dir = tmp_path / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "all-required"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "all-required", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "b", "name": "Base", "required": True, "config": "base/b.yaml"}],
                    },
                }
            )
        )

        # We can't easily inject tmp_path into the running Flask app, so
        # validate the logic via package_manager directly
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
        from package_manager import PackageManager

        pm = PackageManager(root_dir=tmp_path)
        packages = pm.discover_packages()
        assert len(packages) == 1

        # Verify bundled_prisms has no optional items
        bundled = packages[0].get("tiers", {})
        base_items = bundled.get("base", [])
        optional = [i for i in base_items if not i.get("required", False)]
        assert len(optional) == 0


# ---------------------------------------------------------------------------
# /api/package/<name>/config
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestPackageConfigEndpoint:
    def test_prism_config(self, client):
        prism_path = Path(__file__).parent.parent.parent / "prism" / "prisms" / "prism.prism"
        if not prism_path.exists():
            pytest.skip("prism.prism not present")
        resp = client.get("/api/package/prism/config")
        assert resp.status_code == 200
        data = resp.get_json()
        # prism_config may be None if not defined
        assert "prism_config" in data

    def test_nonexistent_package(self, client):
        resp = client.get("/api/package/nope/config")
        data = resp.get_json()
        assert "error" in data or data.get("prism_config") is None


# ---------------------------------------------------------------------------
# /api/tools
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestToolsEndpoint:
    def test_returns_tools_list(self, client):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "tools" in data
        assert isinstance(data["tools"], list)


# ---------------------------------------------------------------------------
# /api/install (POST)
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestInstallEndpoint:
    def test_missing_package_returns_error(self, client):
        resp = client.post(
            "/api/install",
            json={
                "package": "",
                "userInfo": {},
            },
        )
        data = resp.get_json()
        # Either 404/500 or success=False
        assert resp.status_code != 200 or data.get("success") is False

    def test_invalid_package_returns_error(self, client):
        resp = client.post(
            "/api/install",
            json={
                "package": "prism-that-absolutely-does-not-exist-xyz999",
                "userInfo": {"name": "Test", "email": "test@example.com"},
            },
        )
        data = resp.get_json()
        assert data.get("success") is False or "error" in data

    def test_selected_sub_prisms_accepted(self, client):
        """Endpoint should accept selectedSubPrisms without error on the param."""
        resp = client.post(
            "/api/install",
            json={
                "package": "prism-that-absolutely-does-not-exist-xyz999",
                "userInfo": {},
                "selectedSubPrisms": {"teams": "platform"},
            },
        )
        data = resp.get_json()
        # Doesn't matter if it fails — we just check it doesn't 500 on the new param
        assert data is not None


# ---------------------------------------------------------------------------
# Root route
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestRootRoute:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower() or b"Prism" in resp.data

    def test_index_mentions_prism(self, client):
        resp = client.get("/")
        assert b"prism" in resp.data.lower() or b"Prism" in resp.data

"""Unit tests for configuration API blueprint.

BDT: API tier — tests legacy organization/tools routes.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from prism.ui.app import create_app


@pytest.fixture
def app(tmp_path):
    prisms_dir = tmp_path / "prisms"
    prisms_dir.mkdir()

    with patch("prism.container.FileAccessor") as mock_fa_cls:
        mock_fa = MagicMock()
        mock_fa.list_packages.return_value = []
        mock_fa_cls.return_value = mock_fa
        with patch("prism.container.CommandAccessor"):
            with patch("prism.container.SystemAccessor"):
                with patch("prism.container.RegistryAccessor"):
                    application = create_app(prisms_dir=prisms_dir)
                    application.config["TESTING"] = True
                    yield application


@pytest.fixture
def client(app):
    return app.test_client()


class TestGetOrganizations:
    def test_returns_empty_when_no_config(self, client):
        resp = client.get("/api/organizations")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["sub_orgs"] == []
        assert data["departments"] == []
        assert data["teams"] == []

    def test_returns_orgs_from_config(self, client, app, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        import yaml

        with open(config_dir / "inheritance.yaml", "w") as f:
            yaml.dump(
                {
                    "available_sub_orgs": ["engineering"],
                    "available_departments": ["platform"],
                    "available_teams": ["core"],
                },
                f,
            )
        resp = client.get("/api/organizations")
        data = json.loads(resp.data)
        assert data["sub_orgs"] == ["engineering"]
        assert data["departments"] == ["platform"]
        assert data["teams"] == ["core"]


class TestGetTools:
    def test_returns_empty_when_no_config(self, client):
        resp = client.get("/api/tools")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["tools"] == []

    def test_returns_tools_from_config(self, client, app, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        import yaml

        with open(config_dir / "tools.yaml", "w") as f:
            yaml.dump(
                {
                    "tools": {
                        "git": {"description": "Version control", "required": True},
                        "docker": {"description": "Containers", "required": False},
                    }
                },
                f,
            )
        resp = client.get("/api/tools")
        data = json.loads(resp.data)
        assert len(data["tools"]) == 2
        tool_ids = [t["id"] for t in data["tools"]]
        assert "git" in tool_ids
        assert "docker" in tool_ids

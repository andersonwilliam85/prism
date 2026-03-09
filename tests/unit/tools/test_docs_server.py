"""Unit tests for docs server Flask app."""

import pytest

from prism.tools.docs_server.server import create_docs_app


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with a sample project."""
    proj = tmp_path / "my-project"
    proj.mkdir()
    (proj / "README.md").write_text("# My Project\n\nWelcome to my project.")
    (proj / "CONTRIBUTING.md").write_text("# Contributing\n\nHow to help.")
    (proj / "main.py").write_text("pass")
    docs = proj / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# User Guide\n\nStep-by-step instructions.")
    return tmp_path


@pytest.fixture
def client(workspace):
    app = create_docs_app(workspace, branding={"logo_text": "Test Docs", "tagline": "Unit tests"})
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestWelcomePage:
    def test_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_branding(self, client):
        resp = client.get("/")
        assert b"Test Docs" in resp.data

    def test_lists_projects(self, client):
        resp = client.get("/")
        assert b"my-project" in resp.data


class TestProjectPage:
    def test_returns_200(self, client):
        resp = client.get("/project/my-project")
        assert resp.status_code == 200

    def test_shows_readme(self, client):
        resp = client.get("/project/my-project")
        assert b"Welcome to my project" in resp.data

    def test_lists_docs(self, client):
        resp = client.get("/project/my-project")
        assert b"User Guide" in resp.data

    def test_404_unknown_project(self, client):
        resp = client.get("/project/nonexistent")
        assert resp.status_code == 404


class TestDocPage:
    def test_renders_doc(self, client):
        resp = client.get("/doc/my-project/docs/guide.md")
        assert resp.status_code == 200
        assert b"Step-by-step" in resp.data

    def test_404_unknown_doc(self, client):
        resp = client.get("/doc/my-project/docs/nonexistent.md")
        assert resp.status_code == 404


class TestSearch:
    def test_empty_query(self, client):
        resp = client.get("/search")
        assert resp.status_code == 200

    def test_finds_content(self, client):
        resp = client.get("/search?q=Step-by-step")
        assert resp.status_code == 200
        assert b"User Guide" in resp.data

    def test_no_results(self, client):
        resp = client.get("/search?q=xyznonexistent")
        assert resp.status_code == 200
        assert b"No results" in resp.data


class TestApiProjects:
    def test_returns_json(self, client):
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "my-project"
        assert data[0]["has_readme"] is True
        assert "Python" in data[0]["languages"]

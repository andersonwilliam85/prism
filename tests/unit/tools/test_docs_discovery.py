"""Unit tests for DocsDiscoveryEngine."""

from pathlib import Path

import pytest

from prism.tools.docs_server.discovery import DocsDiscoveryEngine


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with sample projects."""
    # Project A — has README and docs/
    proj_a = tmp_path / "project-alpha"
    proj_a.mkdir()
    (proj_a / "README.md").write_text("# Project Alpha\n\nA sample project.")
    (proj_a / "CONTRIBUTING.md").write_text("# Contributing\n\nHow to contribute.")
    (proj_a / "main.py").write_text("print('hello')")
    docs = proj_a / "docs"
    docs.mkdir()
    (docs / "architecture.md").write_text("# Architecture\n\nSystem design.")
    (docs / "setup.md").write_text("# Setup Guide\n\nHow to set up.")

    # Project B — has README only
    proj_b = tmp_path / "project-beta"
    proj_b.mkdir()
    (proj_b / "README.md").write_text("# Project Beta\n\nAnother project.")
    (proj_b / "index.js").write_text("console.log('hi')")

    # Project C — no docs (should be excluded)
    proj_c = tmp_path / "project-gamma"
    proj_c.mkdir()
    (proj_c / "main.go").write_text("package main")

    # Category directory with nested project
    cat = tmp_path / "experiments"
    cat.mkdir()
    nested = cat / "experiment-one"
    nested.mkdir()
    (nested / "README.md").write_text("# Experiment One\n\nA test.")
    (nested / "app.ts").write_text("export default {}")

    # Hidden directory and node_modules (should be skipped)
    hidden = tmp_path / ".hidden-project"
    hidden.mkdir()
    (hidden / "README.md").write_text("# Should Not Appear")
    nm = tmp_path / "node_modules"
    nm.mkdir()
    (nm / "README.md").write_text("# Should Not Appear")

    return tmp_path


class TestDiscovery:
    def test_discovers_projects(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        names = [p.name for p in projects]
        assert "project-alpha" in names
        assert "project-beta" in names

    def test_excludes_hidden_dirs(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        names = [p.name for p in projects]
        assert ".hidden-project" not in names

    def test_excludes_node_modules(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        names = [p.name for p in projects]
        assert "node_modules" not in names

    def test_project_has_readme(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        alpha = next(p for p in projects if p.name == "project-alpha")
        assert alpha.has_readme is True

    def test_discovers_docs_directory(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        alpha = next(p for p in projects if p.name == "project-alpha")
        doc_titles = [d.title for d in alpha.docs]
        assert "Architecture" in doc_titles
        assert "Setup Guide" in doc_titles

    def test_discovers_guide_files(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        alpha = next(p for p in projects if p.name == "project-alpha")
        categories = [d.category for d in alpha.docs]
        assert "guide" in categories

    def test_detects_languages(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        alpha = next(p for p in projects if p.name == "project-alpha")
        assert "Python" in alpha.languages
        beta = next(p for p in projects if p.name == "project-beta")
        assert "JavaScript" in beta.languages

    def test_discovers_nested_projects(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        names = [p.name for p in projects]
        assert "experiment-one" in names

    def test_excludes_projects_without_docs(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        names = [p.name for p in projects]
        # project-gamma has no README or docs — but has a .go file
        # It should be excluded (no docs)
        assert "project-gamma" not in names

    def test_empty_workspace(self, tmp_path):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(tmp_path)
        assert projects == []

    def test_nonexistent_workspace(self):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(Path("/nonexistent/path"))
        assert projects == []

    def test_extracts_title_from_heading(self, workspace):
        engine = DocsDiscoveryEngine()
        projects = engine.discover(workspace)
        alpha = next(p for p in projects if p.name == "project-alpha")
        readme = next(d for d in alpha.docs if d.category == "readme")
        assert readme.title == "Project Alpha"


class TestApiSpecs:
    def test_discovers_openapi_yaml(self, tmp_path):
        proj = tmp_path / "api-service"
        proj.mkdir()
        (proj / "README.md").write_text("# API Service")
        (proj / "openapi.yaml").write_text("openapi: 3.0.0\ninfo:\n  title: Test API")

        engine = DocsDiscoveryEngine()
        projects = engine.discover(tmp_path)
        api_service = next(p for p in projects if p.name == "api-service")
        categories = [d.category for d in api_service.docs]
        assert "api" in categories

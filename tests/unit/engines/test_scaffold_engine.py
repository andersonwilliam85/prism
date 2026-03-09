"""Unit tests for ScaffoldEngine."""

from __future__ import annotations

from prism.engines.scaffold_engine.i_scaffold_engine import IScaffoldEngine
from prism.engines.scaffold_engine.scaffold_engine import ScaffoldEngine


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(ScaffoldEngine(), IScaffoldEngine)


class TestGenerate:
    def test_basic_scaffold(self):
        engine = ScaffoldEngine()
        files = engine.generate("mycompany")
        assert "package.yaml" in files
        assert "teams/platform.yaml" in files
        assert "teams/backend.yaml" in files
        assert "welcome.yaml" in files
        assert "resources.yaml" in files
        assert "mycompany" in files["package.yaml"]

    def test_minimal_scaffold(self):
        engine = ScaffoldEngine()
        files = engine.generate("simple", template="minimal")
        assert "package.yaml" in files
        assert len(files) == 1

    def test_name_sanitization(self):
        engine = ScaffoldEngine()
        files = engine.generate("My Company-config")
        assert "my-company" in files["package.yaml"]

    def test_basic_has_base_config(self):
        engine = ScaffoldEngine()
        files = engine.generate("acme")
        assert "base/acme.yaml" in files

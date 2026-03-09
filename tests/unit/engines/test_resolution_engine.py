"""Unit tests for ResolutionEngine."""

from __future__ import annotations

from prism.engines.resolution_engine.resolution_engine import ResolutionEngine
from prism.engines.resolution_engine.i_resolution_engine import IResolutionEngine


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(ResolutionEngine(), IResolutionEngine)


class TestResolve:
    def test_default_local(self):
        engine = ResolutionEngine()
        result = engine.resolve("startup")
        assert result["type"] == "local"
        assert "startup" in result["local_names"]

    def test_scoped_name_resolves_npm(self):
        engine = ResolutionEngine()
        result = engine.resolve("@prism/startup-config")
        assert result["type"] == "npm"
        assert result["package_name"] == "@prism/startup-config"

    def test_explicit_local_source(self):
        engine = ResolutionEngine()
        sources = [{"type": "local", "path": "/custom/path"}]
        result = engine.resolve("test", sources=sources)
        assert result["type"] == "local"
        assert result["base_path"] == "/custom/path"

    def test_explicit_npm_source(self):
        engine = ResolutionEngine()
        sources = [{"type": "npm", "registry": "https://custom.registry.com"}]
        result = engine.resolve("test", sources=sources)
        assert result["type"] == "npm"
        assert result["registry_url"] == "https://custom.registry.com"

    def test_url_source(self):
        engine = ResolutionEngine()
        sources = [{"type": "url", "url": "https://example.com/pkg.tar.gz"}]
        result = engine.resolve("test", sources=sources)
        assert result["type"] == "url"
        assert result["url"] == "https://example.com/pkg.tar.gz"

    def test_local_name_variations(self):
        engine = ResolutionEngine()
        result = engine.resolve("my-company")
        names = result["local_names"]
        assert "my-company" in names
        assert "my_company" in names

    def test_strips_config_suffix(self):
        engine = ResolutionEngine()
        result = engine.resolve("startup-config")
        names = result["local_names"]
        assert "startup" in names

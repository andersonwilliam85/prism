"""Unit tests for PrismPackageAccessor."""

from __future__ import annotations

import pytest

from prism.accessors.prism_package_accessor.prism_package_accessor import PrismPackageAccessor


def _create_prism(prisms_dir, dir_name, pkg_name, discoverable=True):
    """Helper: create a minimal prism package in prisms_dir."""
    pkg_dir = prisms_dir / dir_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    yaml_content = f"""package:
  name: "{pkg_name}"
  version: "1.0.0"
  description: "Test prism"
  type: "test"
distribution:
  local:
    discoverable: {str(discoverable).lower()}
"""
    (pkg_dir / "package.yaml").write_text(yaml_content)
    return pkg_dir


@pytest.fixture
def prisms_dir(tmp_path):
    d = tmp_path / "prisms"
    d.mkdir()
    return d


class TestListPackages:
    def test_lists_discoverable_packages(self, prisms_dir):
        _create_prism(prisms_dir, "alpha", "alpha-prism")
        _create_prism(prisms_dir, "beta", "beta-prism")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        packages = accessor.list_packages()
        assert len(packages) == 2
        names = [p["name"] for p in packages]
        assert "alpha-prism" in names
        assert "beta-prism" in names

    def test_skips_non_discoverable_packages(self, prisms_dir):
        _create_prism(prisms_dir, "visible", "visible-prism")
        _create_prism(prisms_dir, "hidden", "hidden-prism", discoverable=False)
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        packages = accessor.list_packages()
        assert len(packages) == 1
        assert packages[0]["name"] == "visible-prism"

    def test_skips_dirs_without_package_yaml(self, prisms_dir):
        (prisms_dir / "no-yaml").mkdir()
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        packages = accessor.list_packages()
        assert len(packages) == 0

    def test_skips_hidden_dirs(self, prisms_dir):
        _create_prism(prisms_dir, ".hidden", "hidden-prism")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        packages = accessor.list_packages()
        assert len(packages) == 0

    def test_returns_empty_when_dir_missing(self, tmp_path):
        accessor = PrismPackageAccessor(prisms_dir=tmp_path / "nonexistent")
        assert accessor.list_packages() == []

    def test_includes_metadata_fields(self, prisms_dir):
        _create_prism(prisms_dir, "test-pkg", "test-prism")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        packages = accessor.list_packages()
        pkg = packages[0]
        assert pkg["name"] == "test-prism"
        assert pkg["version"] == "1.0.0"
        assert pkg["description"] == "Test prism"
        assert pkg["type"] == "test"
        assert "path" in pkg


class TestGetPackageConfig:
    def test_returns_full_config(self, prisms_dir):
        _create_prism(prisms_dir, "my-prism", "my-prism")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        config = accessor.get_package_config("my-prism")
        assert config["package"]["name"] == "my-prism"
        assert config["package"]["version"] == "1.0.0"

    def test_raises_for_missing_package(self, prisms_dir):
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        with pytest.raises(FileNotFoundError, match="Package not found"):
            accessor.get_package_config("nonexistent")


class TestFindPackage:
    def test_finds_by_package_name(self, prisms_dir):
        pkg_dir = _create_prism(prisms_dir, "my-dir", "my-prism-name")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        result = accessor.find_package("my-prism-name")
        assert result == pkg_dir

    def test_finds_by_directory_name(self, prisms_dir):
        pkg_dir = _create_prism(prisms_dir, "dir-name", "different-name")
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        result = accessor.find_package("dir-name")
        assert result == pkg_dir

    def test_returns_none_for_missing(self, prisms_dir):
        accessor = PrismPackageAccessor(prisms_dir=prisms_dir)
        assert accessor.find_package("nonexistent") is None

    def test_returns_none_when_prisms_dir_missing(self, tmp_path):
        accessor = PrismPackageAccessor(prisms_dir=tmp_path / "nope")
        assert accessor.find_package("anything") is None

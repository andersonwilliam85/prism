"""Unit tests for FileAccessor (consolidated from ConfigFile + Filesystem + PrismPackage)."""

from __future__ import annotations

from pathlib import Path

import pytest

from prism.accessors.file_accessor.file_accessor import FileAccessor
from prism.accessors.file_accessor.i_file_accessor import IFileAccessor


@pytest.fixture
def accessor() -> IFileAccessor:
    return FileAccessor()


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(FileAccessor(), IFileAccessor)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


class TestFilesystemOps:
    """Tests for mkdir, copy, rmtree, exists, write_text, read_text."""

    def test_mkdir_creates_directory(self, accessor, tmp_dir):
        target = tmp_dir / "subdir"
        accessor.mkdir(target)
        assert target.is_dir()

    def test_mkdir_creates_parents(self, accessor, tmp_dir):
        target = tmp_dir / "a" / "b" / "c"
        accessor.mkdir(target, parents=True)
        assert target.is_dir()

    def test_exists_true(self, accessor, tmp_dir):
        f = tmp_dir / "file.txt"
        f.write_text("hello")
        assert accessor.exists(f) is True

    def test_exists_false(self, accessor, tmp_dir):
        assert accessor.exists(tmp_dir / "nope") is False

    def test_write_and_read_text(self, accessor, tmp_dir):
        f = tmp_dir / "out.txt"
        accessor.write_text(f, "hello world")
        assert accessor.read_text(f) == "hello world"

    def test_write_text_creates_parents(self, accessor, tmp_dir):
        f = tmp_dir / "deep" / "nested" / "file.txt"
        accessor.write_text(f, "content")
        assert f.read_text() == "content"

    def test_read_text_missing_raises(self, accessor, tmp_dir):
        with pytest.raises(FileNotFoundError):
            accessor.read_text(tmp_dir / "missing.txt")

    def test_copy_file(self, accessor, tmp_dir):
        src = tmp_dir / "src.txt"
        src.write_text("data")
        dst = tmp_dir / "dst.txt"
        accessor.copy(src, dst)
        assert dst.read_text() == "data"

    def test_copy_directory(self, accessor, tmp_dir):
        src_dir = tmp_dir / "srcdir"
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")
        dst_dir = tmp_dir / "dstdir"
        accessor.copy(src_dir, dst_dir)
        assert (dst_dir / "file.txt").read_text() == "content"

    def test_copy_missing_raises(self, accessor, tmp_dir):
        with pytest.raises(FileNotFoundError):
            accessor.copy(tmp_dir / "nope", tmp_dir / "dst")

    def test_rmtree_file(self, accessor, tmp_dir):
        f = tmp_dir / "file.txt"
        f.write_text("bye")
        accessor.rmtree(f)
        assert not f.exists()

    def test_rmtree_directory(self, accessor, tmp_dir):
        d = tmp_dir / "dir"
        d.mkdir()
        (d / "inner.txt").write_text("x")
        accessor.rmtree(d)
        assert not d.exists()

    def test_rmtree_missing_raises(self, accessor, tmp_dir):
        with pytest.raises(FileNotFoundError):
            accessor.rmtree(tmp_dir / "missing")


class TestYamlOps:
    """Tests for read_yaml, write_yaml."""

    def test_read_yaml(self, accessor, tmp_dir):
        f = tmp_dir / "config.yaml"
        f.write_text("key: value\nnested:\n  a: 1\n")
        result = accessor.read_yaml(f)
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_read_yaml_empty_returns_empty_dict(self, accessor, tmp_dir):
        f = tmp_dir / "empty.yaml"
        f.write_text("")
        assert accessor.read_yaml(f) == {}

    def test_read_yaml_missing_raises(self, accessor, tmp_dir):
        with pytest.raises(FileNotFoundError):
            accessor.read_yaml(tmp_dir / "nope.yaml")

    def test_write_yaml(self, accessor, tmp_dir):
        f = tmp_dir / "out.yaml"
        accessor.write_yaml(f, {"key": "value", "list": [1, 2]})
        content = f.read_text()
        assert "key: value" in content

    def test_write_yaml_creates_parents(self, accessor, tmp_dir):
        f = tmp_dir / "deep" / "out.yaml"
        accessor.write_yaml(f, {"a": 1})
        assert f.exists()


class TestPackageDiscovery:
    """Tests for list_packages, get_package_config, find_package."""

    def _create_package(self, prisms_dir: Path, name: str, discoverable: bool = True) -> Path:
        pkg_dir = prisms_dir / name
        pkg_dir.mkdir(parents=True)
        config = (
            f"package:\n"
            f'  name: "{name}"\n'
            f'  version: "1.0.0"\n'
            f'  description: "Test package"\n'
            f'  type: "company"\n'
        )
        if not discoverable:
            config += "distribution:\n  local:\n    discoverable: false\n"
        (pkg_dir / "package.yaml").write_text(config)
        return pkg_dir

    def test_list_packages_empty_dir(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        prisms.mkdir()
        assert accessor.list_packages(prisms) == []

    def test_list_packages_finds_packages(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        self._create_package(prisms, "alpha")
        self._create_package(prisms, "beta")
        result = accessor.list_packages(prisms)
        names = [p["name"] for p in result]
        assert "alpha" in names
        assert "beta" in names

    def test_list_packages_skips_non_discoverable(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        self._create_package(prisms, "visible")
        self._create_package(prisms, "hidden", discoverable=False)
        result = accessor.list_packages(prisms)
        names = [p["name"] for p in result]
        assert "visible" in names
        assert "hidden" not in names

    def test_list_packages_nonexistent_dir(self, accessor, tmp_dir):
        assert accessor.list_packages(tmp_dir / "nope") == []

    def test_get_package_config(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        self._create_package(prisms, "test-pkg")
        config = accessor.get_package_config(prisms, "test-pkg")
        assert config["package"]["name"] == "test-pkg"

    def test_get_package_config_not_found(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        prisms.mkdir()
        with pytest.raises(FileNotFoundError):
            accessor.get_package_config(prisms, "nonexistent")

    def test_find_package_by_name(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        self._create_package(prisms, "findme")
        result = accessor.find_package(prisms, "findme")
        assert result is not None
        assert result.name == "findme"

    def test_find_package_by_dir_name(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        pkg_dir = prisms / "mydir"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "package.yaml").write_text(
            'package:\n  name: "different-name"\n  version: "1.0"\n  description: "x"\n'
        )
        # Find by dir name (fallback)
        result = accessor.find_package(prisms, "mydir")
        assert result is not None

    def test_find_package_not_found(self, accessor, tmp_dir):
        prisms = tmp_dir / "prisms"
        prisms.mkdir()
        assert accessor.find_package(prisms, "nope") is None

"""Unit tests for ConfigFileAccessor."""

from __future__ import annotations

import pytest
import yaml

from prism.accessors.config_file_accessor.config_file_accessor import ConfigFileAccessor


@pytest.fixture
def accessor():
    return ConfigFileAccessor()


class TestReadYaml:
    def test_reads_valid_yaml(self, accessor, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("name: test\nversion: 1.0\n")
        result = accessor.read_yaml(f)
        assert result == {"name": "test", "version": 1.0}

    def test_reads_nested_yaml(self, accessor, tmp_path):
        f = tmp_path / "nested.yaml"
        f.write_text("package:\n  name: prism\n  tools:\n    - git\n    - node\n")
        result = accessor.read_yaml(f)
        assert result["package"]["name"] == "prism"
        assert result["package"]["tools"] == ["git", "node"]

    def test_returns_empty_dict_for_empty_file(self, accessor, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        result = accessor.read_yaml(f)
        assert result == {}

    def test_returns_empty_dict_for_non_dict_yaml(self, accessor, tmp_path):
        f = tmp_path / "list.yaml"
        f.write_text("- item1\n- item2\n")
        result = accessor.read_yaml(f)
        assert result == {}

    def test_raises_file_not_found(self, accessor, tmp_path):
        with pytest.raises(FileNotFoundError):
            accessor.read_yaml(tmp_path / "nonexistent.yaml")

    def test_raises_on_invalid_yaml(self, accessor, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text(":\n  :\n    - [invalid: yaml: content")
        with pytest.raises(yaml.YAMLError):
            accessor.read_yaml(f)


class TestWriteYaml:
    def test_writes_yaml_file(self, accessor, tmp_path):
        f = tmp_path / "output.yaml"
        data = {"name": "test", "version": "1.0"}
        accessor.write_yaml(f, data)
        assert f.exists()
        with open(f) as fh:
            loaded = yaml.safe_load(fh)
        assert loaded == data

    def test_creates_parent_dirs(self, accessor, tmp_path):
        f = tmp_path / "deep" / "nested" / "output.yaml"
        accessor.write_yaml(f, {"key": "value"})
        assert f.exists()

    def test_overwrites_existing_file(self, accessor, tmp_path):
        f = tmp_path / "overwrite.yaml"
        accessor.write_yaml(f, {"old": True})
        accessor.write_yaml(f, {"new": True})
        with open(f) as fh:
            loaded = yaml.safe_load(fh)
        assert loaded == {"new": True}

    def test_roundtrip(self, accessor, tmp_path):
        f = tmp_path / "roundtrip.yaml"
        data = {"package": {"name": "test", "tools": ["git", "node"]}, "version": "2.0"}
        accessor.write_yaml(f, data)
        result = accessor.read_yaml(f)
        assert result == data

"""Unit tests for FilesystemAccessor."""

from __future__ import annotations

import pytest

from prism.accessors.filesystem_accessor.filesystem_accessor import FilesystemAccessor


@pytest.fixture
def accessor():
    return FilesystemAccessor()


class TestMkdir:
    def test_creates_directory(self, accessor, tmp_path):
        d = tmp_path / "newdir"
        accessor.mkdir(d)
        assert d.is_dir()

    def test_creates_nested_parents(self, accessor, tmp_path):
        d = tmp_path / "a" / "b" / "c"
        accessor.mkdir(d, parents=True)
        assert d.is_dir()

    def test_idempotent(self, accessor, tmp_path):
        d = tmp_path / "existing"
        d.mkdir()
        accessor.mkdir(d)  # Should not raise
        assert d.is_dir()


class TestCopy:
    def test_copies_file(self, accessor, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        dst = tmp_path / "dst.txt"
        accessor.copy(src, dst)
        assert dst.read_text() == "hello"

    def test_copies_directory_tree(self, accessor, tmp_path):
        src_dir = tmp_path / "src_dir"
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")
        (src_dir / "sub").mkdir()
        (src_dir / "sub" / "nested.txt").write_text("nested")

        dst_dir = tmp_path / "dst_dir"
        accessor.copy(src_dir, dst_dir)
        assert (dst_dir / "file.txt").read_text() == "content"
        assert (dst_dir / "sub" / "nested.txt").read_text() == "nested"

    def test_raises_for_missing_source(self, accessor, tmp_path):
        with pytest.raises(FileNotFoundError):
            accessor.copy(tmp_path / "nonexistent", tmp_path / "dst")


class TestRmtree:
    def test_removes_directory(self, accessor, tmp_path):
        d = tmp_path / "to_remove"
        d.mkdir()
        (d / "file.txt").write_text("data")
        accessor.rmtree(d)
        assert not d.exists()

    def test_removes_single_file(self, accessor, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data")
        accessor.rmtree(f)
        assert not f.exists()

    def test_raises_for_missing_path(self, accessor, tmp_path):
        with pytest.raises(FileNotFoundError):
            accessor.rmtree(tmp_path / "nonexistent")


class TestExists:
    def test_returns_true_for_existing_file(self, accessor, tmp_path):
        f = tmp_path / "exists.txt"
        f.write_text("yes")
        assert accessor.exists(f) is True

    def test_returns_true_for_existing_dir(self, accessor, tmp_path):
        assert accessor.exists(tmp_path) is True

    def test_returns_false_for_missing(self, accessor, tmp_path):
        assert accessor.exists(tmp_path / "nope") is False


class TestWriteText:
    def test_writes_content(self, accessor, tmp_path):
        f = tmp_path / "write.txt"
        accessor.write_text(f, "hello world")
        assert f.read_text() == "hello world"

    def test_creates_parent_dirs(self, accessor, tmp_path):
        f = tmp_path / "deep" / "path" / "file.txt"
        accessor.write_text(f, "nested content")
        assert f.read_text() == "nested content"


class TestReadText:
    def test_reads_content(self, accessor, tmp_path):
        f = tmp_path / "read.txt"
        f.write_text("hello")
        assert accessor.read_text(f) == "hello"

    def test_raises_for_missing_file(self, accessor, tmp_path):
        with pytest.raises(FileNotFoundError):
            accessor.read_text(tmp_path / "nonexistent.txt")

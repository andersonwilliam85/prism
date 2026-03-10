"""Unit tests for RollbackAccessor — file persistence and execution."""

from __future__ import annotations

from pathlib import Path

from prism.accessors.rollback_accessor.rollback_accessor import RollbackAccessor
from prism.models.installation import RollbackAction, RollbackState


class TestSaveAndLoadState:
    def test_round_trip(self, tmp_path: Path) -> None:
        accessor = RollbackAccessor()
        state = RollbackState(package_name="test-prism")
        state.record(RollbackAction(action_type="file_created", target="/tmp/a.txt"))
        state.record(RollbackAction(action_type="dir_created", target="/tmp/dir"))

        path = accessor.save_state(state)
        loaded = accessor.load_state(path)

        assert loaded is not None
        assert loaded.package_name == "test-prism"
        assert len(loaded.actions) == 2
        assert loaded.actions[0].action_type == "file_created"
        assert loaded.actions[1].target == "/tmp/dir"

        # Cleanup
        Path(path).unlink()

    def test_load_missing_file(self) -> None:
        accessor = RollbackAccessor()
        assert accessor.load_state("/nonexistent/path.json") is None

    def test_load_corrupt_file(self, tmp_path: Path) -> None:
        accessor = RollbackAccessor()
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")
        assert accessor.load_state(str(bad_file)) is None


class TestDeleteFile:
    def test_deletes_existing_file(self, tmp_path: Path) -> None:
        accessor = RollbackAccessor()
        f = tmp_path / "test.txt"
        f.write_text("data")
        assert accessor.delete_file(str(f)) is True
        assert not f.exists()

    def test_returns_false_for_missing(self) -> None:
        accessor = RollbackAccessor()
        assert accessor.delete_file("/nonexistent/file.txt") is False


class TestDeleteDirectory:
    def test_deletes_existing_dir(self, tmp_path: Path) -> None:
        accessor = RollbackAccessor()
        d = tmp_path / "subdir"
        d.mkdir()
        (d / "file.txt").write_text("data")
        assert accessor.delete_directory(str(d)) is True
        assert not d.exists()

    def test_returns_false_for_missing(self) -> None:
        accessor = RollbackAccessor()
        assert accessor.delete_directory("/nonexistent/dir") is False


class TestRunCommand:
    def test_successful_command(self) -> None:
        accessor = RollbackAccessor()
        ok, output = accessor.run_command("echo hello")
        assert ok is True
        assert "hello" in output

    def test_failed_command(self) -> None:
        accessor = RollbackAccessor()
        ok, output = accessor.run_command("false")
        assert ok is False

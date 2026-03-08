"""Tests for prism.utilities.progress_logger."""

from unittest.mock import MagicMock

from prism.utilities.progress_logger import LEVEL_PREFIXES, log


class TestLog:
    def test_default_level(self, capsys):
        log("step1", "hello")
        captured = capsys.readouterr()
        assert LEVEL_PREFIXES["info"] in captured.out
        assert "hello" in captured.out

    def test_success_level(self, capsys):
        log("step1", "done", level="success")
        captured = capsys.readouterr()
        assert LEVEL_PREFIXES["success"] in captured.out

    def test_error_level(self, capsys):
        log("step1", "fail", level="error")
        captured = capsys.readouterr()
        assert LEVEL_PREFIXES["error"] in captured.out

    def test_callback_invoked(self):
        cb = MagicMock()
        log("step1", "msg", "info", callback=cb)
        cb.assert_called_once_with("step1", "msg", "info")

    def test_no_callback(self, capsys):
        log("step1", "msg")  # should not raise
        assert "msg" in capsys.readouterr().out

    def test_unknown_level_uses_info_prefix(self, capsys):
        log("step1", "msg", level="debug")
        captured = capsys.readouterr()
        assert LEVEL_PREFIXES["info"] in captured.out

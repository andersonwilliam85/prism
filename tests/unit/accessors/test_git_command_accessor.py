"""Unit tests for GitCommandAccessor."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from prism.accessors.git_command_accessor.git_command_accessor import GitCommandAccessor


@pytest.fixture
def accessor():
    return GitCommandAccessor()


class TestSetConfig:
    @patch("prism.accessors.git_command_accessor.git_command_accessor.subprocess.run")
    def test_sets_global_config(self, mock_run, accessor):
        accessor.set_config("user.name", "Test User")
        mock_run.assert_called_once_with(
            ["git", "config", "--global", "user.name", "Test User"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.git_command_accessor.git_command_accessor.subprocess.run")
    def test_sets_local_config(self, mock_run, accessor):
        accessor.set_config("user.email", "test@example.com", scope="local")
        mock_run.assert_called_once_with(
            ["git", "config", "--local", "user.email", "test@example.com"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch(
        "prism.accessors.git_command_accessor.git_command_accessor.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_raises_file_not_found_when_git_missing(self, mock_run, accessor):
        with pytest.raises(FileNotFoundError, match="git is not installed"):
            accessor.set_config("user.name", "Test")

    @patch(
        "prism.accessors.git_command_accessor.git_command_accessor.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "git"),
    )
    def test_raises_on_command_failure(self, mock_run, accessor):
        with pytest.raises(subprocess.CalledProcessError):
            accessor.set_config("bad.key", "value")


class TestClone:
    @patch("prism.accessors.git_command_accessor.git_command_accessor.subprocess.run")
    def test_clones_repository(self, mock_run, accessor):
        target = Path("/tmp/test-repo")
        accessor.clone("https://github.com/org/repo.git", target)
        mock_run.assert_called_once_with(
            ["git", "clone", "https://github.com/org/repo.git", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch(
        "prism.accessors.git_command_accessor.git_command_accessor.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_raises_file_not_found_when_git_missing(self, mock_run, accessor):
        with pytest.raises(FileNotFoundError, match="git is not installed"):
            accessor.clone("https://github.com/org/repo.git", Path("/tmp/repo"))

    @patch(
        "prism.accessors.git_command_accessor.git_command_accessor.subprocess.run",
        side_effect=subprocess.CalledProcessError(128, "git clone"),
    )
    def test_raises_on_clone_failure(self, mock_run, accessor):
        with pytest.raises(subprocess.CalledProcessError):
            accessor.clone("https://bad-url.example.com/repo.git", Path("/tmp/repo"))

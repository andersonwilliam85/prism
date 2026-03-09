"""Unit tests for CommandAccessor (consolidated from Git + SSH + PlatformPackage)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from prism.accessors.command_accessor.command_accessor import CommandAccessor


@pytest.fixture
def accessor(tmp_path):
    return CommandAccessor(ssh_dir=tmp_path / ".ssh")


class TestGitCommands:
    """Tests for git_set_config, git_clone."""

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_git_set_config(self, mock_run, accessor):
        accessor.git_set_config("user.name", "Test User")
        mock_run.assert_called_once_with(
            ["git", "config", "--global", "user.name", "Test User"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_git_set_config_local_scope(self, mock_run, accessor):
        accessor.git_set_config("user.email", "test@co.com", scope="local")
        mock_run.assert_called_once_with(
            ["git", "config", "--local", "user.email", "test@co.com"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run", side_effect=FileNotFoundError)
    def test_git_set_config_not_installed(self, mock_run, accessor):
        with pytest.raises(FileNotFoundError, match="git is not installed"):
            accessor.git_set_config("user.name", "Test")

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_git_clone(self, mock_run, accessor, tmp_path):
        target = tmp_path / "repo"
        accessor.git_clone("https://github.com/test/repo.git", target)
        mock_run.assert_called_once_with(
            ["git", "clone", "https://github.com/test/repo.git", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )


class TestSSHCommands:
    """Tests for ssh_generate_key, ssh_key_exists."""

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_ssh_generate_key(self, mock_run, accessor, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        key_path = accessor.ssh_generate_key(key_type="ed25519", comment="test@co.com")
        assert key_path == ssh_dir / "id_ed25519"
        assert ssh_dir.exists()
        mock_run.assert_called_once()

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run", side_effect=FileNotFoundError)
    def test_ssh_generate_key_not_installed(self, mock_run, accessor):
        with pytest.raises(FileNotFoundError, match="ssh-keygen"):
            accessor.ssh_generate_key()

    def test_ssh_key_exists_false(self, accessor):
        assert accessor.ssh_key_exists() is False

    def test_ssh_key_exists_true(self, accessor, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir(parents=True)
        (ssh_dir / "id_ed25519").write_text("key")
        assert accessor.ssh_key_exists() is True


class TestPackageCommands:
    """Tests for pkg_install, pkg_is_installed."""

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_pkg_install_mac(self, mock_run, accessor):
        result = accessor.pkg_install("git", "mac")
        assert result is True
        mock_run.assert_called_once_with(
            ["brew", "install", "git"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run")
    def test_pkg_install_windows(self, mock_run, accessor):
        accessor.pkg_install("git", "windows")
        mock_run.assert_called_once_with(
            ["choco", "install", "git", "-y"],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_pkg_install_unsupported_platform(self, accessor):
        with pytest.raises(ValueError, match="Unsupported platform"):
            accessor.pkg_install("git", "freebsd")

    @patch("prism.accessors.command_accessor.command_accessor.subprocess.run", side_effect=FileNotFoundError)
    def test_pkg_install_failure(self, mock_run, accessor):
        result = accessor.pkg_install("git", "mac")
        assert result is False

    @patch("prism.accessors.command_accessor.command_accessor.shutil.which", return_value="/usr/bin/git")
    def test_pkg_is_installed_true(self, mock_which, accessor):
        assert accessor.pkg_is_installed("git") is True

    @patch("prism.accessors.command_accessor.command_accessor.shutil.which", return_value=None)
    def test_pkg_is_installed_false(self, mock_which, accessor):
        assert accessor.pkg_is_installed("nonexistent") is False

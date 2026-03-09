"""Unit tests for SSHKeyAccessor."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from prism.accessors.ssh_key_accessor.ssh_key_accessor import SSHKeyAccessor


class TestGenerateKey:
    @patch("prism.accessors.ssh_key_accessor.ssh_key_accessor.subprocess.run")
    def test_generates_ed25519_key(self, mock_run, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        result = accessor.generate_key()
        assert result == ssh_dir / "id_ed25519"
        mock_run.assert_called_once_with(
            ["ssh-keygen", "-t", "ed25519", "-f", str(ssh_dir / "id_ed25519"), "-N", ""],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.ssh_key_accessor.ssh_key_accessor.subprocess.run")
    def test_generates_rsa_key_with_comment(self, mock_run, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        result = accessor.generate_key(key_type="rsa", comment="user@example.com")
        assert result == ssh_dir / "id_rsa"
        mock_run.assert_called_once_with(
            ["ssh-keygen", "-t", "rsa", "-f", str(ssh_dir / "id_rsa"), "-N", "", "-C", "user@example.com"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.ssh_key_accessor.ssh_key_accessor.subprocess.run")
    def test_creates_ssh_directory(self, mock_run, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        accessor.generate_key()
        assert ssh_dir.is_dir()

    @patch(
        "prism.accessors.ssh_key_accessor.ssh_key_accessor.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_raises_when_ssh_keygen_missing(self, mock_run, tmp_path):
        accessor = SSHKeyAccessor(ssh_dir=tmp_path / ".ssh")
        with pytest.raises(FileNotFoundError, match="ssh-keygen is not installed"):
            accessor.generate_key()


class TestKeyExists:
    def test_returns_true_when_ed25519_exists(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_ed25519").write_text("key")
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        assert accessor.key_exists() is True

    def test_returns_true_when_rsa_exists(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_rsa").write_text("key")
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        assert accessor.key_exists() is True

    def test_returns_false_when_no_keys(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        accessor = SSHKeyAccessor(ssh_dir=ssh_dir)
        assert accessor.key_exists() is False

    def test_returns_false_when_dir_missing(self, tmp_path):
        accessor = SSHKeyAccessor(ssh_dir=tmp_path / "nonexistent")
        assert accessor.key_exists() is False

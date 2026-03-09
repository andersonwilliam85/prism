"""Unit tests for PlatformPackageAccessor."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from prism.accessors.platform_package_accessor.platform_package_accessor import PlatformPackageAccessor


@pytest.fixture
def accessor():
    return PlatformPackageAccessor()


class TestInstall:
    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run")
    def test_installs_via_brew_on_mac(self, mock_run, accessor):
        result = accessor.install("git", "mac")
        assert result is True
        mock_run.assert_called_once_with(
            ["brew", "install", "git"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run")
    def test_installs_via_choco_on_windows(self, mock_run, accessor):
        result = accessor.install("git", "windows")
        assert result is True
        mock_run.assert_called_once_with(
            ["choco", "install", "git", "-y"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run")
    def test_installs_via_apt_on_ubuntu(self, mock_run, accessor):
        result = accessor.install("git", "ubuntu")
        assert result is True
        mock_run.assert_called_once_with(
            ["sudo", "apt-get", "install", "-y", "git"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run")
    def test_installs_via_apt_on_linux(self, mock_run, accessor):
        result = accessor.install("node", "linux")
        assert result is True
        mock_run.assert_called_once_with(
            ["sudo", "apt-get", "install", "-y", "node"],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_raises_for_unsupported_platform(self, accessor):
        with pytest.raises(ValueError, match="Unsupported platform"):
            accessor.install("git", "freebsd")

    @patch(
        "prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "brew"),
    )
    def test_returns_false_on_command_failure(self, mock_run, accessor):
        result = accessor.install("nonexistent-pkg", "mac")
        assert result is False

    @patch(
        "prism.accessors.platform_package_accessor.platform_package_accessor.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_returns_false_when_package_manager_missing(self, mock_run, accessor):
        result = accessor.install("git", "mac")
        assert result is False


class TestIsInstalled:
    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.shutil.which", return_value="/usr/bin/git")
    def test_returns_true_when_on_path(self, mock_which, accessor):
        assert accessor.is_installed("git") is True
        mock_which.assert_called_once_with("git")

    @patch("prism.accessors.platform_package_accessor.platform_package_accessor.shutil.which", return_value=None)
    def test_returns_false_when_not_on_path(self, mock_which, accessor):
        assert accessor.is_installed("nonexistent") is False

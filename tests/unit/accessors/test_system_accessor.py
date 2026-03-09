"""Unit tests for SystemAccessor."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from prism.accessors.system_accessor.i_system_accessor import ISystemAccessor
from prism.accessors.system_accessor.system_accessor import SystemAccessor


@pytest.fixture
def accessor() -> ISystemAccessor:
    return SystemAccessor()


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(SystemAccessor(), ISystemAccessor)


class TestGetPlatform:
    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Darwin")
    @patch("prism.accessors.system_accessor.system_accessor.platform.machine", return_value="arm64")
    def test_detects_mac_apple_silicon(self, mock_machine, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "mac"
        assert detail == "Apple Silicon"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Darwin")
    @patch("prism.accessors.system_accessor.system_accessor.platform.machine", return_value="x86_64")
    def test_detects_mac_intel(self, mock_machine, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "mac"
        assert detail == "Intel"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Windows")
    @patch("prism.accessors.system_accessor.system_accessor.platform.version", return_value="10.0.19041")
    def test_detects_windows(self, mock_version, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "windows"
        assert detail == "10.0.19041"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Linux")
    @patch("prism.accessors.system_accessor.system_accessor.platform.version", return_value="5.4.0")
    @patch("builtins.open", mock_open(read_data="NAME=Ubuntu\nVERSION=20.04"))
    def test_detects_ubuntu(self, mock_version, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "ubuntu"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Linux")
    @patch("prism.accessors.system_accessor.system_accessor.platform.version", return_value="5.4.0")
    @patch("builtins.open", side_effect=OSError)
    def test_detects_generic_linux_when_os_release_missing(self, mock_open, mock_version, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "linux"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="FreeBSD")
    def test_returns_unknown_for_unsupported(self, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "unknown"
        assert detail == ""


class TestGetInstalledVersion:
    @patch("prism.accessors.system_accessor.system_accessor.shutil.which", return_value="/usr/bin/git")
    @patch("prism.accessors.system_accessor.system_accessor.subprocess.run")
    def test_returns_version_string(self, mock_run, mock_which, accessor):
        mock_run.return_value = MagicMock(stdout="git version 2.39.0\n", stderr="")
        result = accessor.get_installed_version("git")
        assert result == "git version 2.39.0"

    @patch("prism.accessors.system_accessor.system_accessor.shutil.which", return_value=None)
    def test_returns_none_when_tool_not_found(self, mock_which, accessor):
        assert accessor.get_installed_version("nonexistent") is None

    @patch("prism.accessors.system_accessor.system_accessor.shutil.which", return_value="/usr/bin/tool")
    @patch(
        "prism.accessors.system_accessor.system_accessor.subprocess.run",
        side_effect=OSError("spawn failed"),
    )
    def test_returns_none_on_subprocess_error(self, mock_run, mock_which, accessor):
        assert accessor.get_installed_version("broken-tool") is None


class TestGetEnv:
    def test_reads_existing_var(self, accessor):
        os.environ["PRISM_TEST_VAR"] = "test_value"
        try:
            assert accessor.get_env("PRISM_TEST_VAR") == "test_value"
        finally:
            del os.environ["PRISM_TEST_VAR"]

    def test_returns_default_for_missing_var(self, accessor):
        assert accessor.get_env("PRISM_NONEXISTENT_VAR_12345", "fallback") == "fallback"

    def test_returns_empty_string_as_default(self, accessor):
        assert accessor.get_env("PRISM_NONEXISTENT_VAR_12345") == ""


class TestSetEnv:
    def test_sets_env_var(self, accessor):
        accessor.set_env("PRISM_TEST_SET", "hello")
        try:
            assert os.environ["PRISM_TEST_SET"] == "hello"
        finally:
            del os.environ["PRISM_TEST_SET"]


class TestGetAllProxyVars:
    def test_returns_set_proxy_vars(self, accessor):
        os.environ["HTTP_PROXY"] = "http://proxy:8080"
        os.environ["HTTPS_PROXY"] = "https://proxy:8443"
        try:
            result = accessor.get_all_proxy_vars()
            assert result["HTTP_PROXY"] == "http://proxy:8080"
            assert result["HTTPS_PROXY"] == "https://proxy:8443"
        finally:
            del os.environ["HTTP_PROXY"]
            del os.environ["HTTPS_PROXY"]

    def test_excludes_unset_vars(self, accessor):
        # Clean any proxy vars that might be set
        for key in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"]:
            os.environ.pop(key, None)
        result = accessor.get_all_proxy_vars()
        assert "HTTP_PROXY" not in result
        assert "ALL_PROXY" not in result

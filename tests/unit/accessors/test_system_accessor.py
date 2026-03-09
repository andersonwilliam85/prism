"""Unit tests for SystemAccessor."""

from __future__ import annotations

import os
from unittest.mock import patch

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
    def test_mac_arm(self, mock_machine, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "mac"
        assert detail == "Apple Silicon"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Darwin")
    @patch("prism.accessors.system_accessor.system_accessor.platform.machine", return_value="x86_64")
    def test_mac_intel(self, mock_machine, mock_system, accessor):
        name, detail = accessor.get_platform()
        assert name == "mac"
        assert detail == "Intel"

    @patch("prism.accessors.system_accessor.system_accessor.platform.system", return_value="Windows")
    @patch("prism.accessors.system_accessor.system_accessor.platform.version", return_value="10.0")
    def test_windows(self, mock_version, mock_system, accessor):
        name, _ = accessor.get_platform()
        assert name == "windows"


class TestGetInstalledVersion:
    @patch("prism.accessors.system_accessor.system_accessor.shutil.which", return_value=None)
    def test_tool_not_found(self, mock_which, accessor):
        assert accessor.get_installed_version("nonexistent") is None

    @patch("prism.accessors.system_accessor.system_accessor.subprocess.run")
    @patch("prism.accessors.system_accessor.system_accessor.shutil.which", return_value="/usr/bin/git")
    def test_tool_version(self, mock_which, mock_run, accessor):
        mock_run.return_value.stdout = "git version 2.40.1\n"
        mock_run.return_value.stderr = ""
        result = accessor.get_installed_version("git")
        assert result == "git version 2.40.1"


class TestEnvVars:
    def test_get_env_exists(self, accessor):
        os.environ["TEST_PRISM_VAR"] = "hello"
        try:
            assert accessor.get_env("TEST_PRISM_VAR") == "hello"
        finally:
            del os.environ["TEST_PRISM_VAR"]

    def test_get_env_default(self, accessor):
        assert accessor.get_env("NONEXISTENT_VAR_12345", "fallback") == "fallback"

    def test_set_env(self, accessor):
        accessor.set_env("TEST_PRISM_SET", "world")
        try:
            assert os.environ["TEST_PRISM_SET"] == "world"
        finally:
            del os.environ["TEST_PRISM_SET"]

    def test_get_all_proxy_vars(self, accessor):
        os.environ["HTTP_PROXY"] = "http://proxy:8080"
        try:
            proxies = accessor.get_all_proxy_vars()
            assert "HTTP_PROXY" in proxies
            assert proxies["HTTP_PROXY"] == "http://proxy:8080"
        finally:
            del os.environ["HTTP_PROXY"]

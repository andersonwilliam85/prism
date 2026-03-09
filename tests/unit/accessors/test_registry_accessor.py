"""Unit tests for RegistryAccessor (renamed from NPMRegistryAccessor)."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from prism.accessors.registry_accessor.registry_accessor import RegistryAccessor
from prism.accessors.registry_accessor.i_registry_accessor import IRegistryAccessor


@pytest.fixture
def accessor() -> IRegistryAccessor:
    return RegistryAccessor(timeout=5)


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(RegistryAccessor(), IRegistryAccessor)


class TestFetchPackage:
    @patch("prism.accessors.registry_accessor.registry_accessor.urllib.request.urlopen")
    def test_fetch_success(self, mock_urlopen, accessor):
        response_data = {"name": "test-pkg", "version": "1.0.0"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = accessor.fetch_package("test-pkg", "https://registry.npmjs.org")
        assert result["name"] == "test-pkg"

    @patch("prism.accessors.registry_accessor.registry_accessor.urllib.request.urlopen")
    def test_fetch_connection_error(self, mock_urlopen, accessor):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        with pytest.raises(ConnectionError):
            accessor.fetch_package("test-pkg", "https://bad-registry.example.com")

    @patch("prism.accessors.registry_accessor.registry_accessor.urllib.request.urlopen")
    def test_fetch_invalid_json(self, mock_urlopen, accessor):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            accessor.fetch_package("test-pkg", "https://registry.npmjs.org")


class TestTestConnection:
    @patch("prism.accessors.registry_accessor.registry_accessor.urllib.request.urlopen")
    def test_connection_success(self, mock_urlopen, accessor):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        assert accessor.test_connection("https://registry.npmjs.org") is True

    @patch("prism.accessors.registry_accessor.registry_accessor.urllib.request.urlopen", side_effect=Exception)
    def test_connection_failure(self, mock_urlopen, accessor):
        assert accessor.test_connection("https://bad.example.com") is False

"""Unit tests for NPMRegistryAccessor."""

from __future__ import annotations

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prism.accessors.npm_registry_accessor.npm_registry_accessor import NPMRegistryAccessor


@pytest.fixture
def accessor():
    return NPMRegistryAccessor(timeout=5)


class TestFetchPackage:
    @patch("prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen")
    def test_fetches_package_metadata(self, mock_urlopen, accessor):
        response_data = {"name": "@prism-dx/test", "version": "1.0.0"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = accessor.fetch_package("@prism-dx/test", "https://registry.npmjs.org")
        assert result == response_data

    @patch(
        "prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen",
        side_effect=urllib.error.URLError("Connection refused"),
    )
    def test_raises_connection_error_on_url_error(self, mock_urlopen, accessor):
        with pytest.raises(ConnectionError, match="Cannot reach registry"):
            accessor.fetch_package("@prism-dx/test", "https://unreachable.example.com")

    @patch("prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen")
    def test_raises_value_error_on_invalid_json(self, mock_urlopen, accessor):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            accessor.fetch_package("@prism-dx/test", "https://registry.npmjs.org")

    @patch("prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen")
    def test_strips_trailing_slash_from_url(self, mock_urlopen, accessor):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"name": "test"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        accessor.fetch_package("@prism-dx/test", "https://registry.npmjs.org/")
        # Verify the request was constructed correctly (no double slash)
        call_args = mock_urlopen.call_args
        request_obj = call_args[0][0]
        assert request_obj.full_url == "https://registry.npmjs.org/@prism-dx/test"


class TestTestConnection:
    @patch("prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen")
    def test_returns_true_on_success(self, mock_urlopen, accessor):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        assert accessor.test_connection("https://registry.npmjs.org") is True

    @patch(
        "prism.accessors.npm_registry_accessor.npm_registry_accessor.urllib.request.urlopen",
        side_effect=urllib.error.URLError("timeout"),
    )
    def test_returns_false_on_failure(self, mock_urlopen, accessor):
        assert accessor.test_connection("https://unreachable.example.com") is False

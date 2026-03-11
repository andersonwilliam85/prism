"""NPMRegistryAccessor — HTTP fetch from npm/unpkg.

Pure I/O translation: sends HTTP requests to npm registry endpoints
and returns parsed responses. No business logic.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class NPMRegistryAccessor:
    """Concrete implementation of INPMRegistryAccessor."""

    def __init__(self, timeout: int = 10):
        """Initialize with optional timeout.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self._timeout = timeout

    def fetch_package(self, package_name: str, registry_url: str) -> dict:
        """Fetch package metadata from an npm registry.

        Args:
            package_name: Full npm package name (e.g. "@prism/prism-config").
            registry_url: Base registry URL (e.g. "https://registry.npmjs.org").

        Returns:
            Package metadata dictionary from the registry.

        Raises:
            ConnectionError: If the registry is unreachable.
            ValueError: If the response is not valid JSON.
        """
        url = f"{registry_url.rstrip('/')}/{package_name}"
        try:
            request = urllib.request.Request(url)
            request.add_header("Accept", "application/json")
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError(f"Unexpected response type from registry for {package_name}")
                return data
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach registry at {registry_url}: {e}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from registry for {package_name}: {e}") from e

    def test_connection(self, registry_url: str) -> bool:
        """Test whether the registry is reachable.

        Args:
            registry_url: Base registry URL to test.

        Returns:
            True if the registry responds, False otherwise.
        """
        try:
            request = urllib.request.Request(registry_url.rstrip("/"))
            request.add_header("Accept", "application/json")
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return response.status == 200
        except Exception:
            return False

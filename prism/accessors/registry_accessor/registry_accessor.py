"""RegistryAccessor — HTTP registry protocol access.

Pure I/O translation: sends HTTP requests to package registries.
No business logic.

Volatility: medium — registry protocol may evolve.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class RegistryAccessor:
    """Concrete implementation of IRegistryAccessor."""

    def __init__(self, timeout: int = 10):
        self._timeout = timeout

    def fetch_package(self, package_name: str, registry_url: str) -> dict:
        """Fetch package metadata from a registry."""
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
        """Test whether a registry is reachable."""
        try:
            request = urllib.request.Request(registry_url.rstrip("/"))
            request.add_header("Accept", "application/json")
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return response.status == 200
        except Exception:
            return False

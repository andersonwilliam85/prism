"""INPMRegistryAccessor — HTTP fetch from npm/unpkg.

Volatility: medium — registry protocol may evolve.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class INPMRegistryAccessor(Protocol):
    def fetch_package(self, package_name: str, registry_url: str) -> dict: ...

    def test_connection(self, registry_url: str) -> bool: ...

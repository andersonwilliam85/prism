"""IRegistryAccessor — HTTP registry protocol access.

Renamed from NPMRegistryAccessor. Named after the logical resource
(registry), not the technology (npm).

Volatility: medium — registry protocol may evolve, new registry types.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IRegistryAccessor(Protocol):
    def fetch_package(self, package_name: str, registry_url: str) -> dict: ...

    def test_connection(self, registry_url: str) -> bool: ...

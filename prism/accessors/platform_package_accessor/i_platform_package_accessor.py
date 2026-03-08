"""IPlatformPackageAccessor — brew/choco/apt command execution.

Volatility: medium — new package managers for new platforms.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IPlatformPackageAccessor(Protocol):
    def install(self, package_name: str, platform_name: str) -> bool: ...

    def is_installed(self, package_name: str) -> bool: ...

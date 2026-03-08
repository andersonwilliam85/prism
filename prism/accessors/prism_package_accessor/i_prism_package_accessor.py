"""IPrismPackageAccessor — prism directory listing + discovery.

Volatility: medium — discovery changes with source types.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IPrismPackageAccessor(Protocol):
    def list_packages(self) -> list[dict]: ...

    def get_package_config(self, package_name: str) -> dict: ...

    def find_package(self, package_name: str) -> Path | None: ...

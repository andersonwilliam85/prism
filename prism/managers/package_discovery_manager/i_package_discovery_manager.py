"""IPackageDiscoveryManager — orchestrates package browsing, metadata, and validation.

Volatility: medium — query interface stable, but validation rules
evolve as the prism schema gains new fields.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.package_info import PackageInfo, TierInfo, UserField


@runtime_checkable
class IPackageDiscoveryManager(Protocol):
    def list_packages(self) -> list[PackageInfo]: ...

    def get_info(self, package_name: str) -> PackageInfo: ...

    def get_tiers(self, package_name: str) -> dict[str, list[TierInfo]]: ...

    def get_user_fields(self, package_name: str) -> list[UserField]: ...

    def validate(self, package_name: str) -> tuple[bool, list[str], list[str]]: ...

    def validate_all(self) -> dict[str, tuple[bool, list[str], list[str]]]: ...

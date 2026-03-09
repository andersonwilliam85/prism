"""IPackageManager — orchestrate package browsing, metadata, and user fields.

Absorbs UserInfoManager (same volatility axis — user fields are
package metadata that changes when the prism schema evolves).

Renamed from PackageDiscoveryManager (compound name → 1 word + suffix).

Volatility: medium — query interface stable; schema evolves.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.package_info import PackageInfo, TierInfo, UserField


@runtime_checkable
class IPackageManager(Protocol):
    # --- Package discovery ---

    def list_packages(self) -> list[PackageInfo]: ...

    def get_info(self, package_name: str) -> PackageInfo: ...

    def get_tiers(self, package_name: str) -> dict[str, list[TierInfo]]: ...

    def validate(self, package_name: str) -> tuple[bool, list[str], list[str]]: ...

    def validate_all(self) -> dict[str, tuple[bool, list[str], list[str]]]: ...

    # --- User info (absorbed from UserInfoManager) ---

    def get_user_fields(self, package_name: str) -> list[UserField]: ...

    def get_user_defaults(self, package_name: str) -> dict[str, str]: ...

    def validate_user_input(self, data: dict[str, str], fields: list[UserField]) -> tuple[bool, list[str]]: ...

"""Manager interfaces — one per manager.

Managers are thin orchestrators. Each interface groups all operations
for a single manager. Faceting is deferred until observed volatility
divergence justifies the split.

Volatility analysis:
  InstallationManager  — low-vol (pipeline step order is stable)
  PackageDiscoveryManager — med-vol (query + validation evolve with schema)
  UserInfoManager — med-vol (field schema + validation evolve with UX)
  PreflightManager — low-vol (environment checks are stable)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import InstallationResult
from prism.models.package_info import PackageInfo, TierInfo, UserField
from prism.models.prism_config import PrismConfig


@runtime_checkable
class IInstallationManager(Protocol):
    """Orchestrates the multi-step installation pipeline.

    Volatility: low — step ordering and pipeline structure rarely change.
    """

    def install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str] | None = None,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> InstallationResult: ...

    def load_prism_config(self, package_name: str) -> PrismConfig: ...

    def merge_tiers(
        self,
        base_config: dict,
        selected_sub_prisms: dict[str, str],
    ) -> dict: ...

    def set_progress_callback(self, callback: object | None) -> None: ...

    def log(self, step: str, message: str, level: str = "info") -> None: ...


@runtime_checkable
class IPackageDiscoveryManager(Protocol):
    """Orchestrates package browsing, metadata, and validation.

    Volatility: medium — query interface stable, but validation rules
    evolve as the prism schema gains new fields.
    """

    def list_packages(self) -> list[PackageInfo]: ...

    def get_info(self, package_name: str) -> PackageInfo: ...

    def get_tiers(self, package_name: str) -> dict[str, list[TierInfo]]: ...

    def get_user_fields(self, package_name: str) -> list[UserField]: ...

    def validate(self, package_name: str) -> tuple[bool, list[str], list[str]]: ...

    def validate_all(self) -> dict[str, tuple[bool, list[str], list[str]]]: ...


@runtime_checkable
class IUserInfoManager(Protocol):
    """Orchestrates user info schema retrieval and input validation.

    Volatility: medium — field definitions and validation rules evolve
    with UX changes and new field types.
    """

    def get_fields(self, package_name: str) -> list[UserField]: ...

    def get_defaults(self, package_name: str) -> dict[str, str]: ...

    def validate(self, data: dict[str, str], fields: list[UserField]) -> tuple[bool, list[str]]: ...


@runtime_checkable
class IPreflightManager(Protocol):
    """Orchestrates environment prerequisite checking.

    Volatility: low — check sequence and pass/fail criteria are stable.
    Separate from InstallationManager because preflight can run
    independently (e.g., UI "is my machine ready?" preview).
    """

    def check(self, requirements: dict) -> tuple[bool, list[str]]: ...

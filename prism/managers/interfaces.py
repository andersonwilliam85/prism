"""Manager interfaces — 4 managers with 9 facets.

Each manager is a thin orchestrator. Facets split the interface by volatility
so consumers only depend on the rate-of-change they care about.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import InstallationPlan, InstallationResult
from prism.models.package_info import PackageInfo, TierInfo, UserField
from prism.models.prism_config import PrismConfig


# ---------------------------------------------------------------------------
# InstallationManager — 3 facets
# ---------------------------------------------------------------------------


@runtime_checkable
class IInstallationSequence(Protocol):
    """Low-vol: step ordering rarely changes."""

    def install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str] | None = None,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> InstallationResult: ...


@runtime_checkable
class IInstallationProgress(Protocol):
    """Med-vol: progress reporting format may change."""

    def set_progress_callback(
        self, callback: object | None
    ) -> None: ...

    def log(self, step: str, message: str, level: str = "info") -> None: ...


@runtime_checkable
class IInstallationConfig(Protocol):
    """Med-vol: how prism config is loaded/merged may change."""

    def load_prism_config(self, package_name: str) -> PrismConfig: ...

    def merge_tiers(
        self,
        base_config: dict,
        selected_sub_prisms: dict[str, str],
    ) -> dict: ...


# ---------------------------------------------------------------------------
# PackageDiscoveryManager — 2 facets
# ---------------------------------------------------------------------------


@runtime_checkable
class IPackageQuery(Protocol):
    """Low-vol: listing and getting packages is stable."""

    def list_packages(self) -> list[PackageInfo]: ...

    def get_info(self, package_name: str) -> PackageInfo: ...

    def get_tiers(self, package_name: str) -> dict[str, list[TierInfo]]: ...

    def get_user_fields(self, package_name: str) -> list[UserField]: ...


@runtime_checkable
class IPackageValidation(Protocol):
    """Med-vol: validation rules evolve with schema."""

    def validate(self, package_name: str) -> tuple[bool, list[str], list[str]]: ...

    def validate_all(self) -> dict[str, tuple[bool, list[str], list[str]]]: ...


# ---------------------------------------------------------------------------
# UserInfoManager — 2 facets
# ---------------------------------------------------------------------------


@runtime_checkable
class IUserInfoSchema(Protocol):
    """Med-vol: field definitions evolve with UX."""

    def get_fields(self, package_name: str) -> list[UserField]: ...

    def get_defaults(self, package_name: str) -> dict[str, str]: ...


@runtime_checkable
class IUserInfoValidation(Protocol):
    """Med-vol: validation rules change with field types."""

    def validate(
        self, data: dict[str, str], fields: list[UserField]
    ) -> tuple[bool, list[str]]: ...


# ---------------------------------------------------------------------------
# PreflightManager — 1 facet
# ---------------------------------------------------------------------------


@runtime_checkable
class IPreflightValidation(Protocol):
    """Low-vol: environment checks are stable."""

    def check(
        self, requirements: dict,
    ) -> tuple[bool, list[str]]: ...

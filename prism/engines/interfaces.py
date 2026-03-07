"""Engine interfaces — 10 engines.

Engines encapsulate volatile business logic. They never do I/O and never
call other engines. Managers compose them.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IConfigMergeEngine(Protocol):
    """Deep merge strategies, level merging, array strategies."""

    def merge(self, base: dict, override: dict) -> dict: ...

    def merge_tiers(
        self, base_config: dict, tier_configs: list[dict]
    ) -> dict: ...


@runtime_checkable
class IValidationEngine(Protocol):
    """Prism schema validation, field checks."""

    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]: ...


@runtime_checkable
class IToolResolutionEngine(Protocol):
    """tools_selected/excluded filtering, platform dispatch logic."""

    def resolve(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> list[dict]: ...


@runtime_checkable
class IScaffoldEngine(Protocol):
    """Template generation for new prisms."""

    def generate(self, name: str, template: str = "basic") -> dict[str, str]: ...


@runtime_checkable
class IPreflightEngine(Protocol):
    """Version comparison, requires checking."""

    def check_requirements(
        self, requirements: dict, installed_versions: dict[str, str]
    ) -> tuple[bool, list[str]]: ...

    def version_satisfies(
        self, installed: str, required: str
    ) -> bool: ...


@runtime_checkable
class IGitConfigEngine(Protocol):
    """Merge git config from prism + user info into config commands."""

    def prepare(
        self, user_info: dict, merged_config: dict
    ) -> list[tuple[str, str]]: ...


@runtime_checkable
class IWorkspaceEngine(Protocol):
    """Determine folder hierarchy from merged config."""

    def plan(self, merged_config: dict) -> list[str]: ...


@runtime_checkable
class IRepoCloneEngine(Protocol):
    """Parse repo URLs, determine clone targets."""

    def plan(
        self, merged_config: dict, workspace_root: str
    ) -> list[dict]: ...


@runtime_checkable
class IPackageSourcingEngine(Protocol):
    """Resolve local vs remote prism source."""

    def resolve(
        self, package_name: str, sources: list[dict] | None = None
    ) -> dict: ...


@runtime_checkable
class IUserInfoValidationEngine(Protocol):
    """Validate user values against field constraints."""

    def validate(
        self, data: dict[str, str], fields: list[dict]
    ) -> tuple[bool, list[str]]: ...

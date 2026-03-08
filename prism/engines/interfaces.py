"""Engine interfaces.

Engines encapsulate volatile business logic. They never do I/O and never
call other engines. Managers compose them.

Volatility analysis — each engine isolates a distinct rate of change:
  ConfigMergeEngine     — high (merge strategies change quarterly)
  ValidationEngine      — medium (evolves with prism schema)
  ToolResolutionEngine  — medium (filtering logic changes with platform support)
  ScaffoldEngine        — low (template structure is stable)
  PreflightEngine       — low (version comparison is stable)
  SetupPlanEngine       — low (git config, workspace, repo planning change together)
  PackageSourcingEngine — medium (source resolution changes with registry support)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IConfigMergeEngine(Protocol):
    """Deep merge strategies, level merging, array strategies.

    Volatility: high — merge rules change as prism schema evolves.
    """

    def merge(self, base: dict, override: dict) -> dict: ...

    def merge_tiers(self, base_config: dict, tier_configs: list[dict]) -> dict: ...


@runtime_checkable
class IValidationEngine(Protocol):
    """Prism schema validation, field checks.

    Volatility: medium — new schema fields require new validation rules.
    """

    def validate(self, config: dict) -> tuple[bool, list[str], list[str]]: ...


@runtime_checkable
class IToolResolutionEngine(Protocol):
    """tools_selected/excluded filtering, platform dispatch logic.

    Volatility: medium — changes when new platforms or tool categories added.
    """

    def resolve(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> list[dict]: ...


@runtime_checkable
class IScaffoldEngine(Protocol):
    """Template generation for new prisms.

    Volatility: low — scaffold structure is stable once established.
    """

    def generate(self, name: str, template: str = "basic") -> dict[str, str]: ...


@runtime_checkable
class IPreflightEngine(Protocol):
    """Version comparison, requires checking.

    Volatility: low — comparison logic rarely changes.
    """

    def check_requirements(self, requirements: dict, installed_versions: dict[str, str]) -> tuple[bool, list[str]]: ...

    def version_satisfies(self, installed: str, required: str) -> bool: ...


@runtime_checkable
class ISetupPlanEngine(Protocol):
    """Plan git config, workspace folders, and repo clones.

    Consolidated from GitConfigEngine + WorkspaceEngine + RepoCloneEngine.
    These share the same volatility axis: all change when the installation
    pipeline's setup phase changes.

    Volatility: low — setup planning logic is stable.
    """

    def plan_git_config(self, user_info: dict, merged_config: dict) -> list[tuple[str, str]]: ...

    def plan_workspace(self, merged_config: dict) -> list[str]: ...

    def plan_repo_clones(self, merged_config: dict, workspace_root: str) -> list[dict]: ...


@runtime_checkable
class IPackageSourcingEngine(Protocol):
    """Resolve local vs remote prism source.

    Volatility: medium — changes as new registry/source types are supported.
    """

    def resolve(self, package_name: str, sources: list[dict] | None = None) -> dict: ...

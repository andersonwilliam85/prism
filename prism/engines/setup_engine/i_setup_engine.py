"""ISetupEngine — plan installation steps, resolve tools, check readiness.

Consolidates SetupPlanEngine + ToolResolutionEngine + PreflightEngine.
All three share the same volatility axis: the installation contract.
They change when "what we install and how we verify readiness" changes.

Volatility: low-medium — installation surface evolves slowly.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ISetupEngine(Protocol):
    # --- Planning ---

    def plan_git_config(self, user_info: dict, merged_config: dict) -> list[tuple[str, str]]: ...

    def plan_workspace(self, merged_config: dict) -> list[str]: ...

    def plan_repo_clones(self, merged_config: dict, workspace_root: str) -> list[dict]: ...

    # --- Tool resolution ---

    def resolve_tools(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> list[dict]: ...

    # --- Preflight checks ---

    def check_requirements(self, requirements: dict, installed_versions: dict[str, str]) -> tuple[bool, list[str]]: ...

    def version_satisfies(self, installed: str, required: str) -> bool: ...

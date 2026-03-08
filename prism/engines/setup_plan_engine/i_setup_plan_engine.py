"""ISetupPlanEngine — plan git config, workspace folders, and repo clones.

Consolidated from GitConfigEngine + WorkspaceEngine + RepoCloneEngine.
These share the same volatility axis: all change when the installation
pipeline's setup phase changes.

Volatility: low — setup planning logic is stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ISetupPlanEngine(Protocol):
    def plan_git_config(self, user_info: dict, merged_config: dict) -> list[tuple[str, str]]: ...

    def plan_workspace(self, merged_config: dict) -> list[str]: ...

    def plan_repo_clones(self, merged_config: dict, workspace_root: str) -> list[dict]: ...

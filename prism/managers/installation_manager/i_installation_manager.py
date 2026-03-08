"""IInstallationManager — orchestrates the multi-step installation pipeline.

Volatility: low — step ordering and pipeline structure rarely change.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.installation import InstallationResult
from prism.models.prism_config import PrismConfig


@runtime_checkable
class IInstallationManager(Protocol):
    def install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str] | None = None,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> InstallationResult: ...

    def load_prism_config(self, package_name: str) -> PrismConfig: ...

    def merge_tiers(self, base_config: dict, selected_sub_prisms: dict[str, str]) -> dict: ...

    def set_progress_callback(self, callback: object | None) -> None: ...

    def log(self, step: str, message: str, level: str = "info") -> None: ...

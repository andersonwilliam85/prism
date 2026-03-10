"""IInstallationManager — orchestrate install pipeline.

Thin orchestrator: loads config, validates, merges, delegates to engine.

Volatility: low — pipeline structure is stable.
"""

from __future__ import annotations

import threading
from typing import Protocol, runtime_checkable

from prism.models.installation import InstallationResult, PrivilegedStep, ProgressCallback
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
        skip_privileged: bool = False,
    ) -> InstallationResult: ...

    def install_privileged(self, steps: list[PrivilegedStep], platform_name: str) -> InstallationResult: ...

    def rollback(self) -> list[dict]: ...

    def check_readiness(self, requirements: dict) -> tuple[bool, list[str]]: ...

    def set_cancel_event(self, event: threading.Event) -> None: ...

    def set_progress_callback(self, callback: ProgressCallback) -> None: ...

    def load_prism_config(self, package_name: str) -> PrismConfig: ...

    def merge_tiers(self, config: dict, selected_sub_prisms: dict[str, str]) -> dict: ...

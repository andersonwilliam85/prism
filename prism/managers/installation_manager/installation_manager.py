"""InstallationManager — orchestrate the install pipeline.

Thin orchestrator: loads config, validates, merges, delegates execution
to the InstallationEngine. The manager owns the "what" (which package,
which sub-prisms); the engine owns the "how" (git, workspace, tools, etc.).

Volatility: low — pipeline structure and step sequence are stable.
"""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

from prism.accessors.file_accessor.i_file_accessor import IFileAccessor
from prism.engines.config_engine.i_config_engine import IConfigEngine
from prism.engines.installation_engine.i_installation_engine import IInstallationEngine
from prism.models.installation import InstallationResult, InstallContext, PrivilegedStep, ProgressCallback
from prism.models.prism_config import BrandingConfig, PrismConfig, ThemeDefinition
from prism.utilities.event_bus.i_event_bus import IEventBus


class InstallationManager:
    """Orchestrate install pipeline: load → validate → merge → delegate."""

    def __init__(
        self,
        config_engine: IConfigEngine,
        installation_engine: IInstallationEngine,
        file_accessor: IFileAccessor,
        system_accessor: object,  # ISystemAccessor — for platform detection
        event_bus: IEventBus,
        prisms_dir: Path,
    ) -> None:
        self._config = config_engine
        self._engine = installation_engine
        self._files = file_accessor
        self._system = system_accessor
        self._event_bus = event_bus
        self._prisms_dir = prisms_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str] | None = None,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
        skip_privileged: bool = False,
    ) -> InstallationResult:
        """Run the installation pipeline."""
        selected_sub_prisms = selected_sub_prisms or {}

        try:
            return self._do_install(
                package_name, user_info, selected_sub_prisms, tools_selected, tools_excluded, skip_privileged
            )
        except Exception as e:
            result = InstallationResult(success=False, package_name=package_name)
            result.error = str(e)
            result.finished_at = datetime.now()
            self._event_bus.publish("installation.failed", {"package": package_name, "error": str(e)})
            return result

    def _do_install(
        self,
        package_name: str,
        user_info: dict,
        selected_sub_prisms: dict[str, str],
        tools_selected: list[str] | None,
        tools_excluded: list[str] | None,
        skip_privileged: bool,
    ) -> InstallationResult:
        """Internal install logic — separated for clean error handling."""
        # Load config
        config = self._files.get_package_config(self._prisms_dir, package_name)

        # Build tier configs from selected sub-prisms
        tier_configs = self._collect_tier_configs(config, selected_sub_prisms)

        # Validate + merge via ConfigEngine
        is_valid, merged, errors, warnings = self._config.prepare(config, tier_configs)
        if not is_valid:
            result = InstallationResult(success=False, package_name=package_name)
            result.error = f"Validation failed: {'; '.join(errors)}"
            return result

        # Detect platform
        platform_name, platform_detail = self._system.get_platform()

        if platform_name == "unknown":
            result = InstallationResult(success=False, package_name=package_name)
            result.error = "Unsupported platform"
            return result

        # Build workspace root
        workspace_dir = user_info.get("workspace_dir", "")
        workspace_root = Path(workspace_dir).expanduser() if workspace_dir else Path.home() / "workspace"

        # Load prism config for proxy/registry
        prism_config = self._load_prism_config(config)

        # Find package path
        pkg_path = self._files.find_package(self._prisms_dir, package_name)

        # Build context and delegate to engine
        context = InstallContext(
            package_name=package_name,
            config=config,
            merged_config=merged,
            user_info=user_info,
            platform_name=platform_name,
            workspace_root=workspace_root,
            pkg_path=pkg_path,
            tools_selected=tools_selected,
            tools_excluded=tools_excluded,
            skip_privileged=skip_privileged,
            selected_sub_prisms=selected_sub_prisms,
            proxies=prism_config.proxies,
            npm_registry=prism_config.npm_registry,
        )

        result = self._engine.install(context)

        # Publish events
        if result.success:
            self._event_bus.publish("installation.complete", {"package": package_name, "success": True})
        elif result.error and "cancelled" in result.error.lower():
            self._event_bus.publish("installation.cancelled", {"package": package_name})
        elif result.error:
            self._event_bus.publish("installation.failed", {"package": package_name, "error": result.error})

        return result

    def install_privileged(self, steps: list[PrivilegedStep], platform_name: str) -> InstallationResult:
        """Execute deferred privileged install steps (Phase 2)."""
        return self._engine.install_privileged(steps, platform_name)

    def rollback(self) -> list[dict]:
        """Rollback the current installation."""
        results = self._engine.rollback()
        self._event_bus.publish("installation.rolled_back", {"results": results})
        return results

    def check_readiness(self, requirements: dict) -> tuple[bool, list[str]]:
        """Check whether the system meets installation requirements."""
        return self._engine.check_requirements(requirements)

    def set_cancel_event(self, event: threading.Event) -> None:
        """Set a threading Event that signals cancellation."""
        self._engine.set_cancel_event(event)

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """Set the progress callback for UI updates."""
        self._engine.set_progress_callback(callback)

    def load_prism_config(self, package_name: str) -> PrismConfig:
        """Load the prism_config section from a package."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        return self._load_prism_config(config)

    def merge_tiers(self, config: dict, selected_sub_prisms: dict[str, str]) -> dict:
        """Build merged config from selected sub-prisms."""
        tier_configs = self._collect_tier_configs(config, selected_sub_prisms)
        return self._config.merge_tiers({}, tier_configs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _collect_tier_configs(self, config: dict, selected_sub_prisms: dict[str, str]) -> list[dict]:
        """Read sub-prism config files and collect them for merging."""
        bundled = config.get("bundled_prisms", {})
        if not bundled:
            return []

        tier_configs: list[dict] = []
        pkg_name = config.get("package", {}).get("name", "")
        pkg_path = self._files.find_package(self._prisms_dir, pkg_name) if pkg_name else None

        for tier_name, tier_prisms in bundled.items():
            if not isinstance(tier_prisms, list):
                continue
            for sub_prism in tier_prisms:
                if not isinstance(sub_prism, dict):
                    continue
                sub_id = sub_prism.get("id")
                config_file = sub_prism.get("config")
                is_required = sub_prism.get("required", False)
                should_include = is_required or (selected_sub_prisms.get(tier_name) == sub_id)

                if should_include and config_file and pkg_path:
                    config_path = pkg_path / config_file
                    if self._files.exists(config_path):
                        try:
                            tier_configs.append(self._files.read_yaml(config_path))
                        except Exception:
                            pass

        return tier_configs

    def _load_prism_config(self, config: dict) -> PrismConfig:
        """Parse prism_config section from a raw config dict."""
        pc = config.get("prism_config", {})
        branding_raw = pc.get("branding", {})
        custom_themes_raw = pc.get("custom_themes", [])
        custom_themes = []
        for ct in custom_themes_raw:
            if isinstance(ct, dict) and "id" in ct and "name" in ct:
                custom_themes.append(
                    ThemeDefinition(**{k: v for k, v in ct.items() if k in ThemeDefinition.__dataclass_fields__})
                )

        return PrismConfig(
            theme=pc.get("theme", "ocean"),
            theme_options=pc.get("theme_options", []),
            default_theme=pc.get("default_theme", pc.get("theme", "ocean")),
            custom_themes=custom_themes,
            sources=pc.get("sources", []),
            npm_registry=pc.get("npm_registry", ""),
            unpkg_url=pc.get("unpkg_url", ""),
            proxies=pc.get("proxies", {}),
            branding=(
                BrandingConfig(**{k: v for k, v in branding_raw.items() if k in BrandingConfig.__dataclass_fields__})
                if branding_raw
                else BrandingConfig()
            ),
        )

"""PackageManager — orchestrate package browsing, metadata, and user fields.

Delegates to ConfigEngine for validation, FileAccessor for I/O.
No direct I/O — all filesystem access goes through the accessor.

Volatility: medium — query interface stable; schema evolves.
"""

from __future__ import annotations

from pathlib import Path

from prism.accessors.file_accessor.i_file_accessor import IFileAccessor
from prism.engines.config_engine.i_config_engine import IConfigEngine
from prism.models.package_info import PackageInfo, TierInfo, UserField


class PackageManager:
    """Concrete implementation of IPackageManager."""

    def __init__(
        self,
        config_engine: IConfigEngine,
        file_accessor: IFileAccessor,
        prisms_dir: Path,
    ) -> None:
        self._config = config_engine
        self._files = file_accessor
        self._prisms_dir = prisms_dir

    # ------------------------------------------------------------------
    # Package discovery
    # ------------------------------------------------------------------

    def list_packages(self) -> list[PackageInfo]:
        """List all discoverable prism packages."""
        raw_packages = self._files.list_packages(self._prisms_dir)
        return [
            PackageInfo(
                name=pkg["name"],
                dir_name=pkg.get("dir_name", pkg["name"]),
                display_name=pkg.get("name", pkg["name"]).replace("-", " ").replace(".", " ").title(),
                version=pkg.get("version", "1.0.0"),
                description=pkg.get("description", ""),
                package_type=pkg.get("type", "prism"),
                default=pkg.get("default", False),
                path=pkg.get("path", ""),
            )
            for pkg in raw_packages
        ]

    def get_info(self, package_name: str) -> PackageInfo:
        """Get metadata for a single package."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        pkg = config.get("package", {})
        bundled = config.get("bundled_prisms", {})
        tools = config.get("tools_required", config.get("tools", []))
        pkg_path = self._files.find_package(self._prisms_dir, package_name)

        return PackageInfo(
            name=pkg.get("name", package_name),
            display_name=pkg.get("name", package_name).replace("-", " ").replace(".", " ").title(),
            version=pkg.get("version", "1.0.0"),
            description=pkg.get("description", ""),
            author=pkg.get("author", ""),
            package_type=pkg.get("type", "prism"),
            has_tiers=bool(bundled),
            has_tools=bool(tools),
            path=str(pkg_path) if pkg_path else "",
        )

    def get_tiers(self, package_name: str) -> dict[str, list[TierInfo]]:
        """Get the bundled_prisms tier structure for a package."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        bundled = config.get("bundled_prisms", {})
        result: dict[str, list[TierInfo]] = {}

        for tier_name, tier_prisms in bundled.items():
            if not isinstance(tier_prisms, list):
                continue
            tier_list: list[TierInfo] = []
            for sub_prism in tier_prisms:
                if not isinstance(sub_prism, dict):
                    continue
                tier_list.append(
                    TierInfo(
                        id=sub_prism.get("id", ""),
                        name=sub_prism.get("name", sub_prism.get("id", "")),
                        required=sub_prism.get("required", False),
                        description=sub_prism.get("description", ""),
                    )
                )
            if tier_list:
                result[tier_name] = tier_list

        return result

    def validate(self, package_name: str) -> tuple[bool, list[str], list[str]]:
        """Validate a single package config."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        return self._config.validate(config)

    def validate_all(self) -> dict[str, tuple[bool, list[str], list[str]]]:
        """Validate all discoverable packages."""
        results: dict[str, tuple[bool, list[str], list[str]]] = {}
        for pkg in self.list_packages():
            try:
                results[pkg.name] = self.validate(pkg.name)
            except FileNotFoundError:
                results[pkg.name] = (False, [f"Package not found: {pkg.name}"], [])
        return results

    # ------------------------------------------------------------------
    # User info
    # ------------------------------------------------------------------

    def get_user_fields(self, package_name: str) -> list[UserField]:
        """Get user info fields for a package."""
        config = self._files.get_package_config(self._prisms_dir, package_name)
        raw_fields = config.get("user_info_fields", [])
        if not isinstance(raw_fields, list):
            return []

        return [
            UserField(
                id=f.get("id", ""),
                label=f.get("label", ""),
                type=f.get("type", "text"),
                required=f.get("required", False),
                placeholder=f.get("placeholder", ""),
                options=f.get("options", []),
                depends_on=f.get("depends_on", ""),
                option_map=f.get("option_map", {}),
            )
            for f in raw_fields
            if isinstance(f, dict) and f.get("id")
        ]

    def get_user_defaults(self, package_name: str) -> dict[str, str]:
        """Get default values for user info fields."""
        fields = self.get_user_fields(package_name)
        return {f.id: f.placeholder for f in fields if f.placeholder}

    def validate_user_input(self, data: dict[str, str], fields: list[UserField]) -> tuple[bool, list[str]]:
        """Validate user-provided data against field definitions."""
        errors: list[str] = []
        for field in fields:
            value = data.get(field.id, "").strip()
            if field.required and not value:
                errors.append(f"Required field missing: {field.label}")
            if field.type == "email" and value and "@" not in value:
                errors.append(f"Invalid email: {field.label}")
            if field.type == "select" and value and field.options and value not in field.options:
                errors.append(f"Invalid selection for {field.label}: {value}")
        return len(errors) == 0, errors

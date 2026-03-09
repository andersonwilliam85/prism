"""PrismPackageAccessor — prism directory listing + discovery.

Pure I/O translation: scans the prisms/ directory for package.yaml files,
parses them, and returns metadata. No business logic beyond reading files.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class PrismPackageAccessor:
    """Concrete implementation of IPrismPackageAccessor."""

    def __init__(self, prisms_dir: Path | None = None):
        """Initialize with the root prisms directory.

        Args:
            prisms_dir: Path to the prisms/ directory.
                        Defaults to <project_root>/prisms/.
        """
        if prisms_dir is not None:
            self._prisms_dir = prisms_dir
        else:
            # Default: assume project root is two levels up from this file
            self._prisms_dir = Path(__file__).parent.parent.parent.parent / "prisms"

    def list_packages(self) -> list[dict]:
        """List all discoverable prism packages.

        Scans the prisms directory for subdirectories containing a
        package.yaml file. Respects the distribution.local.discoverable flag.

        Returns:
            List of package metadata dicts, sorted by name.
        """
        packages: list[dict] = []

        if not self._prisms_dir.exists():
            return packages

        for pkg_dir in sorted(self._prisms_dir.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
                continue

            package_yaml = pkg_dir / "package.yaml"
            if not package_yaml.exists():
                continue

            try:
                with open(package_yaml, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f) or {}

                # Respect discoverable flag
                dist = metadata.get("distribution", {})
                if not dist.get("local", {}).get("discoverable", True):
                    continue

                pkg_info = metadata.get("package", {})
                packages.append(
                    {
                        "name": pkg_info.get("name", pkg_dir.name),
                        "version": pkg_info.get("version", "unknown"),
                        "description": pkg_info.get("description", "No description"),
                        "type": pkg_info.get("type", "unknown"),
                        "path": str(pkg_dir),
                    }
                )
            except (yaml.YAMLError, OSError):
                # Skip packages that cannot be read
                continue

        return packages

    def get_package_config(self, package_name: str) -> dict:
        """Read and return the full package.yaml for a named package.

        Args:
            package_name: The package name (as declared in package.name)
                          or the directory name.

        Returns:
            Parsed package.yaml content as a dict.

        Raises:
            FileNotFoundError: If the package cannot be found.
        """
        pkg_path = self.find_package(package_name)
        if pkg_path is None:
            raise FileNotFoundError(f"Package not found: {package_name}")

        package_yaml = pkg_path / "package.yaml"
        with open(package_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def find_package(self, package_name: str) -> Path | None:
        """Find a package directory by name.

        Tries matching against package.name in each package.yaml first,
        then falls back to directory name matching.

        Args:
            package_name: Package name or directory name.

        Returns:
            Path to the package directory, or None if not found.
        """
        if not self._prisms_dir.exists():
            return None

        # First pass: match on package.name field in package.yaml
        for pkg_dir in sorted(self._prisms_dir.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
                continue
            package_yaml = pkg_dir / "package.yaml"
            if not package_yaml.exists():
                continue
            try:
                with open(package_yaml, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f) or {}
                if metadata.get("package", {}).get("name") == package_name:
                    return pkg_dir
            except (yaml.YAMLError, OSError):
                continue

        # Second pass: match on directory name
        direct_path = self._prisms_dir / package_name
        if direct_path.is_dir() and (direct_path / "package.yaml").exists():
            return direct_path

        return None

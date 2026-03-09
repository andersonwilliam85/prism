"""FileAccessor — local filesystem I/O.

Consolidates ConfigFileAccessor + FilesystemAccessor + PrismPackageAccessor.
Pure I/O translation: reads/writes files, YAML, directories, and prism packages.
No business logic.

Volatility: low — filesystem API is stable.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml


class FileAccessor:
    """Concrete implementation of IFileAccessor."""

    # ------------------------------------------------------------------
    # Filesystem operations
    # ------------------------------------------------------------------

    def mkdir(self, path: Path, parents: bool = True) -> None:
        """Create a directory, optionally including parents."""
        path.mkdir(parents=parents, exist_ok=True)

    def copy(self, src: Path, dst: Path) -> None:
        """Copy a file or directory tree from src to dst."""
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def rmtree(self, path: Path) -> None:
        """Remove a file or directory tree."""
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def exists(self, path: Path) -> bool:
        """Check whether a path exists."""
        return path.exists()

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file, creating parent dirs as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def read_text(self, path: Path) -> str:
        """Read text content from a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # YAML operations
    # ------------------------------------------------------------------

    def read_yaml(self, path: Path) -> dict:
        """Read a YAML file and return its contents as a dict."""
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def write_yaml(self, path: Path, data: dict) -> None:
        """Write a dictionary to a YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    # ------------------------------------------------------------------
    # Package discovery
    # ------------------------------------------------------------------

    def list_packages(self, prisms_dir: Path) -> list[dict]:
        """List all discoverable prism packages in a directory."""
        packages: list[dict] = []

        if not prisms_dir.exists():
            return packages

        for pkg_dir in sorted(prisms_dir.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
                continue

            package_yaml = pkg_dir / "package.yaml"
            if not package_yaml.exists():
                continue

            try:
                with open(package_yaml, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f) or {}

                dist = metadata.get("distribution", {})
                if not dist.get("local", {}).get("discoverable", True):
                    continue

                pkg_info = metadata.get("package", {})
                prism_config = metadata.get("prism_config", {})
                packages.append(
                    {
                        "dir_name": pkg_dir.name,
                        "name": pkg_info.get("name", pkg_dir.name),
                        "version": pkg_info.get("version", "unknown"),
                        "description": pkg_info.get("description", "No description"),
                        "type": pkg_info.get("type", "unknown"),
                        "path": str(pkg_dir),
                        "default": prism_config.get("default", False),
                    }
                )
            except (yaml.YAMLError, OSError):
                continue

        return packages

    def get_package_config(self, prisms_dir: Path, package_name: str) -> dict:
        """Read the full package.yaml for a named package."""
        pkg_path = self.find_package(prisms_dir, package_name)
        if pkg_path is None:
            raise FileNotFoundError(f"Package not found: {package_name}")

        package_yaml = pkg_path / "package.yaml"
        with open(package_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def find_package(self, prisms_dir: Path, package_name: str) -> Path | None:
        """Find a package directory by name."""
        if not prisms_dir.exists():
            return None

        # First pass: match on package.name field
        for pkg_dir in sorted(prisms_dir.iterdir()):
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
        direct_path = prisms_dir / package_name
        if direct_path.is_dir() and (direct_path / "package.yaml").exists():
            return direct_path

        return None

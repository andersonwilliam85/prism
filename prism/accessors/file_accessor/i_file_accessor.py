"""IFileAccessor — local filesystem I/O (files, YAML, directories, packages).

Consolidates ConfigFileAccessor + FilesystemAccessor + PrismPackageAccessor.
All three share the same volatility axis: local filesystem I/O. They change
when file format conventions change (rarely/never).

Volatility: low — filesystem API is stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IFileAccessor(Protocol):
    # --- Filesystem operations ---

    def mkdir(self, path: Path, parents: bool = True) -> None: ...

    def copy(self, src: Path, dst: Path) -> None: ...

    def rmtree(self, path: Path) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def read_text(self, path: Path) -> str: ...

    # --- YAML operations ---

    def read_yaml(self, path: Path) -> dict: ...

    def write_yaml(self, path: Path, data: dict) -> None: ...

    # --- Package discovery ---

    def list_packages(self, prisms_dir: Path) -> list[dict]: ...

    def get_package_config(self, prisms_dir: Path, package_name: str) -> dict: ...

    def find_package(self, prisms_dir: Path, package_name: str) -> Path | None: ...

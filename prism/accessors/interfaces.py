"""Accessor interfaces — 9 accessors.

Accessors encapsulate I/O boundaries. They translate between the system's
domain model and external systems (filesystem, subprocess, network).
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IConfigFileAccessor(Protocol):
    """YAML read/write (centralized)."""

    def read_yaml(self, path: Path) -> dict: ...

    def write_yaml(self, path: Path, data: dict) -> None: ...


@runtime_checkable
class IFilesystemAccessor(Protocol):
    """mkdir, copy, rmtree, exists, write."""

    def mkdir(self, path: Path, parents: bool = True) -> None: ...

    def copy(self, src: Path, dst: Path) -> None: ...

    def rmtree(self, path: Path) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def read_text(self, path: Path) -> str: ...


@runtime_checkable
class IGitCommandAccessor(Protocol):
    """git config, clone subprocess calls."""

    def set_config(self, key: str, value: str, scope: str = "global") -> None: ...

    def clone(self, url: str, target: Path) -> None: ...


@runtime_checkable
class ISSHKeyAccessor(Protocol):
    """ssh-keygen subprocess, key file management."""

    def generate_key(
        self, key_type: str = "ed25519", comment: str = ""
    ) -> Path: ...

    def key_exists(self) -> bool: ...


@runtime_checkable
class IPlatformPackageAccessor(Protocol):
    """brew/choco/apt command execution."""

    def install(self, package_name: str, platform_name: str) -> bool: ...

    def is_installed(self, package_name: str) -> bool: ...


@runtime_checkable
class IPrismPackageAccessor(Protocol):
    """Prism directory listing + discovery."""

    def list_packages(self) -> list[dict]: ...

    def get_package_config(self, package_name: str) -> dict: ...

    def find_package(self, package_name: str) -> Path | None: ...


@runtime_checkable
class INPMRegistryAccessor(Protocol):
    """HTTP fetch from npm/unpkg."""

    def fetch_package(
        self, package_name: str, registry_url: str
    ) -> dict: ...

    def test_connection(self, registry_url: str) -> bool: ...


@runtime_checkable
class ISystemInfoAccessor(Protocol):
    """Platform detection, /etc/os-release."""

    def get_platform(self) -> tuple[str, str]: ...

    def get_installed_version(self, tool_name: str) -> str | None: ...


@runtime_checkable
class IEnvironmentAccessor(Protocol):
    """Read/write environment variables (proxy, etc.)."""

    def get(self, key: str, default: str = "") -> str: ...

    def set(self, key: str, value: str) -> None: ...

    def get_all_proxy_vars(self) -> dict[str, str]: ...

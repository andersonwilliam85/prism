"""ICommandAccessor — CLI subprocess execution (git, ssh, package managers).

Consolidates GitCommandAccessor + SSHKeyAccessor + PlatformPackageAccessor.
All three share the same volatility axis: subprocess CLI execution.
They change when CLI tool interfaces change (rarely).

Volatility: low — CLI tool interfaces are stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ICommandAccessor(Protocol):
    # --- Git commands ---

    def git_set_config(self, key: str, value: str, scope: str = "global") -> None: ...

    def git_clone(self, url: str, target: Path) -> None: ...

    # --- SSH commands ---

    def ssh_generate_key(self, key_type: str = "ed25519", comment: str = "") -> Path: ...

    def ssh_key_exists(self) -> bool: ...

    # --- Package manager commands ---

    def pkg_install(self, package_name: str, platform_name: str) -> bool: ...

    def pkg_is_installed(self, package_name: str) -> bool: ...

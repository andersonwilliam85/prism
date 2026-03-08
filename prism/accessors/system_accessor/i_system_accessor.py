"""ISystemAccessor — platform detection, OS info, and environment variables.

Consolidated from SystemInfoAccessor + EnvironmentAccessor. Both access
OS-level system state and change for the same reason (new platform support).

Volatility: low — OS detection + env vars are stable APIs.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ISystemAccessor(Protocol):
    def get_platform(self) -> tuple[str, str]: ...

    def get_installed_version(self, tool_name: str) -> str | None: ...

    def get_env(self, key: str, default: str = "") -> str: ...

    def set_env(self, key: str, value: str) -> None: ...

    def get_all_proxy_vars(self) -> dict[str, str]: ...

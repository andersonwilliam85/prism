"""IGitCommandAccessor — git config, clone subprocess calls.

Volatility: low — git CLI is stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IGitCommandAccessor(Protocol):
    def set_config(self, key: str, value: str, scope: str = "global") -> None: ...

    def clone(self, url: str, target: Path) -> None: ...

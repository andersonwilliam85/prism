"""IConfigFileAccessor — YAML read/write (centralized).

Volatility: low — YAML format is stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IConfigFileAccessor(Protocol):
    def read_yaml(self, path: Path) -> dict: ...

    def write_yaml(self, path: Path, data: dict) -> None: ...

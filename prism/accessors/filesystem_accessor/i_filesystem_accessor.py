"""IFilesystemAccessor — mkdir, copy, rmtree, exists, write.

Volatility: low — filesystem API is stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class IFilesystemAccessor(Protocol):
    def mkdir(self, path: Path, parents: bool = True) -> None: ...

    def copy(self, src: Path, dst: Path) -> None: ...

    def rmtree(self, path: Path) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def read_text(self, path: Path) -> str: ...

"""ISSHKeyAccessor — ssh-keygen subprocess, key file management.

Volatility: low — ssh-keygen is stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ISSHKeyAccessor(Protocol):
    def generate_key(self, key_type: str = "ed25519", comment: str = "") -> Path: ...

    def key_exists(self) -> bool: ...

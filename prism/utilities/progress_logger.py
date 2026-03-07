"""Progress logging utility.

Extracted from installer_engine.py:187-192. Stateless formatting + callback dispatch.
"""

from __future__ import annotations

from typing import Callable

LEVEL_PREFIXES = {
    "info": "\u2139\ufe0f",
    "success": "\u2705",
    "error": "\u274c",
    "warning": "\u26a0\ufe0f",
}

ProgressCallback = Callable[[str, str, str], None] | None


def log(
    step: str,
    message: str,
    level: str = "info",
    callback: ProgressCallback = None,
) -> None:
    """Log a message with emoji prefix and optionally invoke a callback."""
    prefix = LEVEL_PREFIXES.get(level, LEVEL_PREFIXES["info"])
    print(f"{prefix} {message}")
    if callback is not None:
        callback(step, message, level)

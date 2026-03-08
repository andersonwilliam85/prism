"""Environment variable substitution utility.

Extracted from config_merger.py:203-232. Pure recursive substitution — no I/O.
"""

from __future__ import annotations

import os
import re
from typing import Any

_PATTERN = re.compile(r"\$\{([^}:]+)(?::-([^}]+))?\}")


def substitute(value: Any) -> Any:
    """Recursively substitute ${VAR} and ${VAR:-default} in config values.

    Supports strings, dicts, and lists. Non-string leaves pass through unchanged.
    """
    if isinstance(value, str):
        return _PATTERN.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), value)
    elif isinstance(value, dict):
        return {k: substitute(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [substitute(item) for item in value]
    return value

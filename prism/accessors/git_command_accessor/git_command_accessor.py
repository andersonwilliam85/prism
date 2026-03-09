"""GitCommandAccessor — git config, clone subprocess calls.

Pure I/O translation: wraps subprocess calls to the git CLI.
No business logic — just command execution and error translation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitCommandAccessor:
    """Concrete implementation of IGitCommandAccessor."""

    def set_config(self, key: str, value: str, scope: str = "global") -> None:
        """Set a git config value.

        Args:
            key: Git config key (e.g. "user.name").
            value: Value to set.
            scope: Config scope — "global", "local", or "system".

        Raises:
            subprocess.CalledProcessError: If the git command fails.
            FileNotFoundError: If git is not installed.
        """
        cmd = ["git", "config", f"--{scope}", key, value]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise FileNotFoundError("git is not installed or not on PATH")

    def clone(self, url: str, target: Path) -> None:
        """Clone a git repository to the target directory.

        Args:
            url: Repository URL.
            target: Local directory to clone into.

        Raises:
            subprocess.CalledProcessError: If the clone fails.
            FileNotFoundError: If git is not installed.
        """
        cmd = ["git", "clone", url, str(target)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise FileNotFoundError("git is not installed or not on PATH")

"""RollbackAccessor — persistence and execution for rollback operations.

Saves rollback state to temp files (survives crashes), deletes files/dirs,
and executes rollback commands.

Volatility: low — file I/O and subprocess are stable.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from prism.models.installation import RollbackAction, RollbackState


class RollbackAccessor:
    """Concrete implementation of IRollbackAccessor."""

    def save_state(self, state: RollbackState) -> str:
        """Persist rollback state to a temp file. Returns the file path."""
        data = {
            "package_name": state.package_name,
            "started_at": state.started_at.isoformat(),
            "rolled_back": state.rolled_back,
            "actions": [
                {
                    "action_type": a.action_type,
                    "target": a.target,
                    "rollback_command": a.rollback_command,
                    "original_value": a.original_value,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in state.actions
            ],
        }
        fd, path = tempfile.mkstemp(prefix="prism_rollback_", suffix=".json")
        with open(fd, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def load_state(self, path: str) -> RollbackState | None:
        """Load rollback state from a temp file."""
        p = Path(path)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text())
            actions = [
                RollbackAction(
                    action_type=a["action_type"],
                    target=a["target"],
                    rollback_command=a.get("rollback_command", ""),
                    original_value=a.get("original_value", ""),
                    timestamp=datetime.fromisoformat(a["timestamp"]),
                )
                for a in data.get("actions", [])
            ]
            return RollbackState(
                package_name=data["package_name"],
                actions=actions,
                started_at=datetime.fromisoformat(data["started_at"]),
                rolled_back=data.get("rolled_back", False),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def delete_file(self, path: str) -> bool:
        """Delete a file. Returns True if deleted."""
        p = Path(path)
        if p.is_file():
            p.unlink()
            return True
        return False

    def delete_directory(self, path: str) -> bool:
        """Delete a directory tree. Returns True if deleted."""
        p = Path(path)
        if p.is_dir():
            shutil.rmtree(p)
            return True
        return False

    def run_command(self, command: str) -> tuple[bool, str]:
        """Run a rollback command. Returns (success, output)."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output.strip()
        except (subprocess.TimeoutExpired, OSError) as e:
            return False, str(e)

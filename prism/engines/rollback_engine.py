"""Rollback engine — execute rollback from a persisted manifest.

Shared by the CLI (`prism rollback`) and the API (`/api/rollback`).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def find_manifest(workspace: str | None = None) -> Path | None:
    """Search for .prism_rollback.json in common locations."""
    candidates = []
    if workspace:
        candidates.append(Path(workspace).expanduser() / ".prism_rollback.json")
    candidates.append(Path.home() / ".prism_rollback.json")
    candidates.append(Path.cwd() / ".prism_rollback.json")

    for c in candidates:
        if c.exists():
            return c
    return None


def load_manifest(manifest_path: Path) -> dict:
    """Load and parse a rollback manifest."""
    return json.loads(manifest_path.read_text())


def execute_rollback(manifest: dict, log_fn=None) -> list[dict]:
    """Execute rollback from a manifest, returning results per action.

    Args:
        manifest: parsed .prism_rollback.json content
        log_fn: optional callback(message, level) for progress reporting
    """
    if log_fn is None:
        log_fn = lambda msg, level="info": None  # noqa: E731

    actions = manifest.get("actions", [])
    results = []

    for action in reversed(actions):
        action_type = action["type"]
        target = action["target"]
        rollback_cmd = action.get("rollback_command", "")
        original_value = action.get("original_value", "")

        try:
            if action_type == "tool_installed" and rollback_cmd:
                log_fn(f"Uninstalling {target}...", "info")
                subprocess.run(rollback_cmd, shell=True, check=True, capture_output=True, text=True, timeout=120)
                results.append({"action": target, "type": action_type, "success": True, "detail": "uninstalled"})
                log_fn(f"{target} uninstalled", "success")

            elif action_type == "file_created":
                p = Path(target)
                if p.exists():
                    p.unlink()
                    results.append({"action": target, "type": action_type, "success": True, "detail": "removed"})
                    log_fn(f"Removed {target}", "success")
                else:
                    results.append({"action": target, "type": action_type, "success": True, "detail": "already gone"})

            elif action_type == "dir_created":
                p = Path(target)
                if p.exists():
                    try:
                        p.rmdir()
                        results.append({"action": target, "type": action_type, "success": True, "detail": "removed"})
                        log_fn(f"Removed {target}", "success")
                    except OSError:
                        results.append({"action": target, "type": action_type, "success": False, "detail": "not empty"})
                        log_fn(f"{target} not empty, skipping", "warning")
                else:
                    results.append({"action": target, "type": action_type, "success": True, "detail": "already gone"})

            elif action_type == "config_changed":
                if original_value:
                    subprocess.run(
                        ["git", "config", "--global", target, original_value],
                        check=True,
                        capture_output=True,
                    )
                    results.append(
                        {"action": target, "type": action_type, "success": True, "detail": f"restored={original_value}"}
                    )
                    log_fn(f"Restored {target}={original_value}", "success")
                else:
                    subprocess.run(
                        ["git", "config", "--global", "--unset", target],
                        capture_output=True,
                    )
                    results.append({"action": target, "type": action_type, "success": True, "detail": "unset"})
                    log_fn(f"Unset {target}", "success")

            else:
                results.append({"action": target, "type": action_type, "success": False, "detail": "unknown action"})

        except subprocess.TimeoutExpired:
            results.append({"action": target, "type": action_type, "success": False, "detail": "timed out"})
            log_fn(f"Timed out rolling back {target}", "warning")
        except Exception as e:
            results.append({"action": target, "type": action_type, "success": False, "detail": str(e)})
            log_fn(f"Failed to rollback {target}: {e}", "warning")

    return results

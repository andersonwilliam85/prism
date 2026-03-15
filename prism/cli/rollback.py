"""prism rollback — undo a previous prism installation using the saved manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace, _SubParsersAction
from pathlib import Path


def register(subparsers: _SubParsersAction) -> None:
    """Register the ``rollback`` subcommand."""
    p = subparsers.add_parser(
        "rollback",
        help="Undo a previous prism installation",
        description="Read .prism_rollback.json and reverse all recorded actions.",
    )
    p.add_argument(
        "workspace",
        nargs="?",
        default=None,
        help="Path to the workspace (looks for .prism_rollback.json there)",
    )
    p.set_defaults(func=_run)


def _run(args: Namespace) -> None:
    """Execute rollback from the manifest."""
    workspace = Path(args.workspace).expanduser() if args.workspace else None

    # Search for the manifest
    candidates = []
    if workspace:
        candidates.append(workspace / ".prism_rollback.json")
    candidates.append(Path.home() / ".prism_rollback.json")
    candidates.append(Path.cwd() / ".prism_rollback.json")

    manifest_path = None
    for c in candidates:
        if c.exists():
            manifest_path = c
            break

    if not manifest_path:
        print("  No rollback manifest found (.prism_rollback.json)")
        print("  Provide the workspace path: prism rollback ~/my-workspace")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    actions = manifest.get("actions", [])
    if not actions:
        print("  Manifest has no actions to rollback.")
        sys.exit(0)

    print(f"\n  Rolling back {len(actions)} actions from {manifest_path}\n")

    # Process in reverse order (LIFO)
    for action in reversed(actions):
        action_type = action["type"]
        target = action["target"]
        rollback_cmd = action.get("rollback_command", "")
        original_value = action.get("original_value", "")

        if action_type == "tool_installed" and rollback_cmd:
            print(f"  Uninstalling {target}...")
            try:
                subprocess.run(rollback_cmd, shell=True, check=True, capture_output=True, text=True)
                print(f"    ✓ {target} uninstalled")
            except Exception:
                print(f"    ✗ Failed to uninstall {target}")

        elif action_type == "file_created":
            p = Path(target)
            if p.exists():
                p.unlink()
                print(f"    ✓ Removed {target}")
            else:
                print(f"    - {target} (already gone)")

        elif action_type == "dir_created":
            p = Path(target)
            if p.exists():
                try:
                    p.rmdir()  # Only removes empty dirs
                    print(f"    ✓ Removed {target}")
                except OSError:
                    print(f"    - {target} (not empty, skipping)")
            else:
                print(f"    - {target} (already gone)")

        elif action_type == "config_changed" and original_value:
            try:
                subprocess.run(
                    ["git", "config", "--global", target, original_value],
                    check=True,
                    capture_output=True,
                )
                print(f"    ✓ Restored git config {target}={original_value}")
            except Exception:
                print(f"    ✗ Failed to restore {target}")

        elif action_type == "config_changed" and not original_value:
            try:
                subprocess.run(
                    ["git", "config", "--global", "--unset", target],
                    check=True,
                    capture_output=True,
                )
                print(f"    ✓ Unset git config {target}")
            except Exception:
                print(f"    - git config {target} (already unset)")

        else:
            print(f"    ? Unknown action: {action_type} {target}")

    # Remove the manifest itself
    manifest_path.unlink(missing_ok=True)
    print("\n  Rollback complete. Manifest removed.\n")

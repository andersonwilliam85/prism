"""prism rollback — undo a previous prism installation using the saved manifest."""

from __future__ import annotations

import sys
from argparse import Namespace, _SubParsersAction

from prism.engines.rollback_engine import execute_rollback, find_manifest, load_manifest


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
    manifest_path = find_manifest(args.workspace)

    if not manifest_path:
        print("\n  No rollback manifest found (.prism_rollback.json)")
        print("  Provide the workspace path: prism rollback ~/my-workspace")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    actions = manifest.get("actions", [])

    if not actions:
        print("  Manifest has no actions to rollback.")
        sys.exit(0)

    print(f"\n  Rolling back {len(actions)} actions from {manifest_path}\n")

    def log(msg, level="info"):
        symbols = {"success": "+", "warning": "!", "error": "x", "info": "i"}
        print(f"  [{symbols.get(level, 'i')}] {msg}")

    results = execute_rollback(manifest, log_fn=log)

    manifest_path.unlink(missing_ok=True)
    succeeded = sum(1 for r in results if r["success"])
    print(f"\n  Rollback complete. {succeeded}/{len(results)} actions reversed.\n")

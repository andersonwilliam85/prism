"""prism history — show previous prism installations on this machine."""

from __future__ import annotations

import json
import sys
from argparse import Namespace, _SubParsersAction
from pathlib import Path


def register(subparsers: _SubParsersAction) -> None:
    """Register the ``history`` subcommand."""
    p = subparsers.add_parser(
        "history",
        help="Show previous prism installations",
        description="Scan for .prism_installed and .prism_rollback.json markers.",
    )
    p.add_argument(
        "search_paths",
        nargs="*",
        default=None,
        help="Directories to scan (default: ~, ~/dev, ~/projects, ~/workspace, ~/Development)",
    )
    p.set_defaults(func=_run)


def _find_installs(search_paths: list[Path]) -> list[dict]:
    """Scan directories for prism installation markers."""
    installs = []
    seen = set()

    for base in search_paths:
        if not base.exists():
            continue
        # Check the directory itself
        for marker_name in (".prism_installed", ".prism_rollback.json"):
            marker = base / marker_name
            if marker.exists() and str(base) not in seen:
                seen.add(str(base))
                installs.append(_read_install(base))
                break
        # Check one level deep
        try:
            for child in base.iterdir():
                if not child.is_dir():
                    continue
                for marker_name in (".prism_installed", ".prism_rollback.json"):
                    marker = child / marker_name
                    if marker.exists() and str(child) not in seen:
                        seen.add(str(child))
                        installs.append(_read_install(child))
                        break
        except PermissionError:
            pass

    return installs


def _read_install(workspace: Path) -> dict:
    """Read install info from a workspace directory."""
    info = {"workspace": str(workspace)}

    marker = workspace / ".prism_installed"
    if marker.exists():
        try:
            with open(marker) as f:
                data = json.load(f)
            info["installed_at"] = data.get("installed_at", "unknown")
            info["package"] = data.get("prism", "unknown")
            info["platform"] = data.get("platform", "unknown")
            info["user"] = data.get("user", "unknown")
            info["sub_prisms"] = data.get("selected_sub_prisms", {})
        except (json.JSONDecodeError, OSError):
            info["installed_at"] = "unknown"

    rollback = workspace / ".prism_rollback.json"
    info["has_rollback"] = rollback.exists()
    if rollback.exists():
        try:
            with open(rollback) as f:
                data = json.load(f)
            info["tools_installed"] = [
                a["target"] for a in data.get("actions", []) if a.get("type") == "tool_installed"
            ]
            info["action_count"] = len(data.get("actions", []))
        except (json.JSONDecodeError, OSError):
            pass

    return info


def _run(args: Namespace) -> None:
    """Show install history."""
    home = Path.home()
    if args.search_paths:
        search = [Path(p).expanduser() for p in args.search_paths]
    else:
        search = [
            home,
            home / "dev",
            home / "projects",
            home / "workspace",
            home / "Development",
        ]

    installs = _find_installs(search)

    if not installs:
        print("\n  No prism installations found.\n")
        sys.exit(0)

    print(f"\n  Found {len(installs)} installation(s):\n")
    for i, inst in enumerate(installs, 1):
        print(f"  {i}. {inst['workspace']}")
        if "package" in inst:
            print(f"     Package:   {inst.get('package', '?')}")
        if "installed_at" in inst:
            print(f"     Installed: {inst.get('installed_at', '?')}")
        if "user" in inst:
            print(f"     User:      {inst.get('user', '?')}")
        if inst.get("sub_prisms"):
            for k, v in inst["sub_prisms"].items():
                print(f"     {k}: {v}")
        if inst.get("tools_installed"):
            print(f"     Tools:     {', '.join(inst['tools_installed'])}")
        if inst.get("has_rollback"):
            print(f"     Rollback:  available ({inst.get('action_count', '?')} actions)")
        else:
            print("     Rollback:  not available")
        print()

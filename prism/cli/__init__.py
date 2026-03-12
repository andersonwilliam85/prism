"""Prism CLI — refract complexity into clarity.

Entry point for the ``prism`` command registered via pyproject.toml.
Dispatches to subcommands: install, ui, packages.
"""

from __future__ import annotations

import argparse
import sys

from prism.cli.install import register as register_install
from prism.cli.packages import register as register_packages
from prism.cli.ui import register as register_ui


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prism",
        description="Prism — refract complexity into clarity",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0b1")

    sub = parser.add_subparsers(dest="command")
    register_install(sub)
    register_ui(sub)
    register_packages(sub)

    return parser


def main() -> None:
    """CLI entry point for prism."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Each subcommand registers a ``func`` default on its sub-parser.
    args.func(args)

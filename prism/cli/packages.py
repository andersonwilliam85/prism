"""prism packages — list, validate, and inspect prism packages."""

from __future__ import annotations

import sys
from argparse import Namespace, _SubParsersAction

from prism.container import Container


def register(subparsers: _SubParsersAction) -> None:
    """Register the ``packages`` subcommand."""
    p = subparsers.add_parser(
        "packages",
        help="List, validate, and inspect prism packages",
        description="Manage available prism configuration packages.",
    )
    pkg_sub = p.add_subparsers(dest="packages_command")

    # prism packages list
    ls = pkg_sub.add_parser("list", help="List available prism packages")
    ls.set_defaults(func=_list)

    # prism packages validate [name]
    val = pkg_sub.add_parser("validate", help="Validate a prism package")
    val.add_argument("name", nargs="?", help="Package name (validates all if omitted)")
    val.set_defaults(func=_validate)

    # prism packages info <name>
    info = pkg_sub.add_parser("info", help="Show detailed package information")
    info.add_argument("name", help="Package name")
    info.set_defaults(func=_info)

    p.set_defaults(func=lambda args: p.print_help())


def _list(args: Namespace) -> None:
    """List all available prism packages."""
    container = Container()
    packages = container.package_manager.list_packages()

    if not packages:
        print("No prism packages found.")
        return

    print(f"\n  {'Package':<25} {'Version':<10} Description")
    print(f"  {'-------':<25} {'-------':<10} -----------")
    for pkg in packages:
        default = " *" if pkg.default else ""
        print(f"  {pkg.name + default:<25} {pkg.version:<10} {pkg.description}")
    print()


def _validate(args: Namespace) -> None:
    """Validate prism package(s)."""
    container = Container()

    if args.name:
        try:
            is_valid, errors, warnings = container.package_manager.validate(args.name)
        except FileNotFoundError:
            print(f"Package not found: {args.name}")
            sys.exit(1)

        if is_valid:
            print(f"  {args.name}: Valid")
        else:
            print(f"  {args.name}: Invalid")
            for e in errors:
                print(f"    Error: {e}")
        for w in warnings:
            print(f"    Warning: {w}")
    else:
        results = container.package_manager.validate_all()
        valid_count = sum(1 for v, _, _ in results.values() if v)
        invalid_count = len(results) - valid_count

        for name, (is_valid, errors, warnings) in results.items():
            status = "Valid" if is_valid else "Invalid"
            print(f"  {name}: {status}")
            for e in errors:
                print(f"    Error: {e}")
            for w in warnings:
                print(f"    Warning: {w}")

        print(f"\n  Valid: {valid_count}  Invalid: {invalid_count}")
        if invalid_count > 0:
            sys.exit(1)


def _info(args: Namespace) -> None:
    """Show detailed info for a package."""
    container = Container()

    try:
        pkg = container.package_manager.get_info(args.name)
    except FileNotFoundError:
        print(f"Package not found: {args.name}")
        sys.exit(1)

    print(f"\n  Name:        {pkg.name}")
    print(f"  Version:     {pkg.version}")
    print(f"  Description: {pkg.description}")
    if pkg.author:
        print(f"  Author:      {pkg.author}")
    print(f"  Type:        {pkg.package_type}")
    print(f"  Has tiers:   {pkg.has_tiers}")
    print(f"  Has tools:   {pkg.has_tools}")
    if pkg.path:
        print(f"  Path:        {pkg.path}")
    print()

    # Show tiers if available
    if pkg.has_tiers:
        tiers = container.package_manager.get_tiers(args.name)
        for tier_name, tier_items in tiers.items():
            print(f"  Tier: {tier_name}")
            for item in tier_items:
                req = " (required)" if item.required else ""
                print(f"    - {item.name}{req}")
                if item.description:
                    print(f"      {item.description}")
        print()

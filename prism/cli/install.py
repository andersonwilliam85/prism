"""prism install — interactive CLI installer."""

from __future__ import annotations

import os
import sys
from argparse import Namespace, _SubParsersAction

from prism.container import Container


def register(subparsers: _SubParsersAction) -> None:
    """Register the ``install`` subcommand."""
    p = subparsers.add_parser(
        "install",
        help="Run the interactive developer-environment installer",
        description="Set up your complete dev environment from a prism configuration.",
    )
    p.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    p.add_argument("--status", action="store_true", help="Show current installation progress")
    p.add_argument("--prism", dest="package", help="Prism package to install (e.g. prism, fortune500)")
    p.add_argument("--config", dest="config_file", help="Config file for non-interactive mode")
    p.add_argument("--npm-registry", help="Custom npm registry URL (overrides PRISM_NPM_REGISTRY)")
    p.add_argument("--unpkg-url", help="Custom unpkg CDN URL (overrides PRISM_UNPKG_URL)")
    p.add_argument("--skip-privileged", action="store_true", help="Skip steps that require sudo")
    p.set_defaults(func=_run)


def _run(args: Namespace) -> None:
    """Execute the install subcommand."""
    # Propagate registry overrides to environment
    if args.npm_registry:
        os.environ["PRISM_NPM_REGISTRY"] = args.npm_registry
    if args.unpkg_url:
        os.environ["PRISM_UNPKG_URL"] = args.unpkg_url

    container = Container()

    if args.status:
        _show_status(container)
        return

    # Determine which package to install
    package_name = args.package or _select_package(container)
    if not package_name:
        print("No prism package selected. Exiting.")
        sys.exit(1)

    # Gather user info
    user_info = _gather_user_info(container, package_name, args.config_file)

    # Print banner
    _print_banner(package_name)

    # Run installation
    result = container.installation_manager.install(
        package_name=package_name,
        user_info=user_info,
        skip_privileged=args.skip_privileged,
    )

    if result.success:
        print("\nInstallation complete!")
        print(f"Package: {result.package_name}")
    else:
        print(f"\nInstallation failed: {result.error}")
        sys.exit(1)


def _show_status(container: Container) -> None:
    """Show available packages and their validation status."""
    packages = container.package_manager.list_packages()
    if not packages:
        print("No prism packages found.")
        return

    print("\nAvailable prism packages:\n")
    for pkg in packages:
        print(f"  {pkg.name:<30} {pkg.description}")
    print()


def _select_package(container: Container) -> str | None:
    """Let the user pick a package interactively."""
    packages = container.package_manager.list_packages()
    if not packages:
        print("No prism packages found.")
        return None

    if len(packages) == 1:
        return packages[0].name

    print("\nAvailable prism packages:\n")
    for i, pkg in enumerate(packages, 1):
        default_marker = " (default)" if pkg.default else ""
        print(f"  {i}. {pkg.display_name}{default_marker}")
        if pkg.description:
            print(f"     {pkg.description}")
    print()

    # Try questionary first, fall back to input()
    try:
        import questionary

        choices = [pkg.display_name for pkg in packages]
        selected = questionary.select("Select a prism:", choices=choices).ask()
        if selected is None:
            return None
        idx = choices.index(selected)
        return packages[idx].name
    except ImportError:
        pass

    while True:
        choice = input(f"Select a package (1-{len(packages)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(packages):
            return packages[int(choice) - 1].name
        print("Invalid selection.")


def _gather_user_info(container: Container, package_name: str, config_file: str | None) -> dict:
    """Collect user information interactively or from config file."""
    if config_file:
        import yaml

        with open(config_file) as f:
            return yaml.safe_load(f) or {}

    fields = container.package_manager.get_user_fields(package_name)
    if not fields:
        # Minimal fallback
        name = input("Your name: ").strip()
        email = input("Your email: ").strip()
        return {"name": name, "email": email}

    # Try questionary for rich prompts
    try:
        import questionary

        data: dict[str, str] = {}
        for field in fields:
            if field.type == "select" and field.options:
                answer = questionary.select(field.label, choices=field.options).ask()
            else:
                answer = questionary.text(
                    field.label,
                    default=field.placeholder,
                ).ask()
            if answer is None:
                print("Cancelled.")
                sys.exit(1)
            data[field.id] = answer
        return data
    except ImportError:
        pass

    # Plain input fallback
    data = {}
    for field in fields:
        prompt = f"{field.label}"
        if field.placeholder:
            prompt += f" [{field.placeholder}]"
        prompt += ": "
        value = input(prompt).strip()
        data[field.id] = value or field.placeholder
    return data


def _print_banner(package_name: str) -> None:
    """Print a welcome banner."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print(
            Panel(
                f"[bold blue]Prism Dev Environment Setup[/bold blue]\n\n"
                f"Package: {package_name}\n\n"
                f"[dim]Setting up your complete dev environment...[/dim]",
                title="Prism",
                border_style="blue",
            )
        )
    except ImportError:
        print(f"\n{'=' * 50}")
        print(f"Prism Dev Environment Setup — {package_name}")
        print(f"{'=' * 50}\n")

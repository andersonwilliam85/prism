#!/usr/bin/env python3
"""
Dev Onboarding Package - FULL IMPLEMENTATION

Automated development environment installer for Mac, Windows, and Ubuntu.
Sets up folder structure, tools, git config, SSH keys, and documentation server.

IDEMPOTENT: Can be run multiple times safely. Only installs what's missing.

Usage:
    python3 install.py                    # Interactive setup
    python3 install.py --resume           # Resume from last checkpoint
    python3 install.py --config FILE      # Use config file (non-interactive)
    python3 install.py --status           # Show current progress
"""

import platform
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

# Try to import rich/questionary for better UX
try:
    from rich.console import Console  # noqa: F401
    from rich.table import Table  # noqa: F401

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False

try:
    import questionary  # noqa: F401

    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR / "config"
USER_PROFILE_PATH = CONFIG_DIR / "user-profile.yaml"
TOOLS_CONFIG_PATH = CONFIG_DIR / "tools.yaml"
RESOURCES_CONFIG_PATH = CONFIG_DIR / "resources.yaml"

# ============================================================================
# Utility Functions
# ============================================================================


def run_command(cmd, cwd=None, check=False, capture=True):
    """Run shell command and return result (IDEMPOTENT - returns status)"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=check)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check)
            return result.returncode == 0, "", ""
    except subprocess.CalledProcessError as e:
        return False, getattr(e, "stdout", ""), getattr(e, "stderr", "")
    except Exception as e:
        return False, "", str(e)


def print_step(message, emoji="➡️"):
    """Print a step message"""
    if RICH_AVAILABLE:
        console.print(f"\n{emoji} [bold]{message}[/bold]")
    else:
        print(f"\n{emoji} {message}")


def print_success(message):
    """Print success message"""
    if RICH_AVAILABLE:
        console.print(f"[green]✅ {message}[/green]")
    else:
        print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    if RICH_AVAILABLE:
        console.print(f"[red]❌ {message}[/red]")
    else:
        print(f"❌ {message}")


def print_warning(message):
    """Print warning message"""
    if RICH_AVAILABLE:
        console.print(f"[yellow]⚠️  {message}[/yellow]")
    else:
        print(f"⚠️  {message}")


# ============================================================================
# Platform Detection
# ============================================================================


def detect_platform():
    """Detect operating system"""
    system = platform.system().lower()

    if system == "darwin":
        machine = platform.machine()
        return "mac", "Apple Silicon" if machine == "arm64" else "Intel"
    elif system == "windows":
        return "windows", platform.version()
    elif system == "linux":
        try:
            with open("/etc/os-release") as f:
                if "ubuntu" in f.read().lower():
                    return "ubuntu", platform.version()
        except Exception:
            pass
        return "linux", platform.version()
    else:
        return "unknown", ""


# ============================================================================
# Progress Tracking (IDEMPOTENT)
# ============================================================================


def load_progress():
    """Load setup progress from user profile"""
    if not USER_PROFILE_PATH.exists():
        return None

    with open(USER_PROFILE_PATH) as f:
        profile = yaml.safe_load(f)

    return profile.get("setup_progress", {})


def save_progress(task_name, notes="", success=True):
    """Save task completion to progress tracker"""
    # Load or initialize profile
    if USER_PROFILE_PATH.exists():
        with open(USER_PROFILE_PATH) as f:
            profile = yaml.safe_load(f)
    else:
        # Create from template
        template_path = CONFIG_DIR / "user-profile.yaml"
        with open(template_path) as f:
            profile = yaml.safe_load(f)

    if "setup_progress" not in profile:
        profile["setup_progress"] = {"status": "in_progress", "started_at": datetime.now().isoformat(), "tasks": {}}

    profile["setup_progress"]["tasks"][task_name] = {
        "completed": success,
        "timestamp": datetime.now().isoformat(),
        "notes": notes,
    }
    profile["setup_progress"]["last_updated"] = datetime.now().isoformat()

    # Save
    USER_PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_PROFILE_PATH, "w") as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False)


def is_task_completed(task_name):
    """Check if a task is already completed (IDEMPOTENT)"""
    progress = load_progress()
    if not progress:
        return False

    task = progress.get("tasks", {}).get(task_name, {})
    return task.get("completed", False)


def show_progress():
    """Display current setup progress"""
    progress = load_progress()

    if not progress or not progress.get("tasks"):
        print("❌ No setup progress found. Run: python3 install.py")
        return

    if RICH_AVAILABLE:
        table = Table(title="📊 Setup Progress")
        table.add_column("Task", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Completed", style="dim")

        for task, data in progress.get("tasks", {}).items():
            status = "✅" if data.get("completed") else "⏳"
            timestamp = data.get("timestamp", "")
            if timestamp:
                timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")

            table.add_row(task.replace("_", " ").title(), status, timestamp)

        console.print(table)
    else:
        print("\n📊 Setup Progress:\n")
        for task, data in progress.get("tasks", {}).items():
            status = "✅" if data.get("completed") else "⏳"
            print(f"  {status} {task.replace('_', ' ').title()}")
        print()


# I'll continue in the next message due to length...

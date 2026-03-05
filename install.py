#!/usr/bin/env python3
"""
Dev Onboarding Package

Automated development environment installer for Mac, Windows, and Ubuntu.
Sets up folder structure, tools, git config, SSH keys, and documentation server.

Fully standalone CLI installer!

Usage:
    python3 install.py                    # Interactive setup
    python3 install.py --resume           # Resume from last checkpoint
    python3 install.py --config FILE      # Use config file (non-interactive)
    python3 install.py --status           # Show current progress
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import yaml
import shutil

# Try to import rich for better UX
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  For better experience, install: pip3 install rich questionary pyyaml")
    print("   Continuing with basic interface...\n")

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR / "config"
USER_PROFILE_PATH = CONFIG_DIR / "user-profile.yaml"
TOOLS_CONFIG_PATH = CONFIG_DIR / "tools.yaml"

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
        # Check if Ubuntu
        try:
            with open("/etc/os-release") as f:
                if "ubuntu" in f.read().lower():
                    return "ubuntu", platform.version()
        except:
            pass
        return "linux", platform.version()
    else:
        return "unknown", ""

# ============================================================================
# Progress Tracking
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
    if not USER_PROFILE_PATH.exists():
        # Initialize profile
        profile = yaml.safe_load(open(CONFIG_DIR / "user-profile.yaml"))
    else:
        with open(USER_PROFILE_PATH) as f:
            profile = yaml.safe_load(f)
    
    if "setup_progress" not in profile:
        profile["setup_progress"] = {
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "tasks": {}
        }
    
    profile["setup_progress"]["tasks"][task_name] = {
        "completed": success,
        "timestamp": datetime.now().isoformat(),
        "notes": notes
    }
    profile["setup_progress"]["last_updated"] = datetime.now().isoformat()
    
    with open(USER_PROFILE_PATH, 'w') as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

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

# ============================================================================
# Banner
# ============================================================================

def print_banner(platform_name, platform_detail):
    """Print welcome banner"""
    if RICH_AVAILABLE:
        console.print(Panel(
            f"[bold blue]🐶 Dev Environment Setup[/bold blue]\n\n"
            f"Platform: {platform_name.title()} ({platform_detail})\n\n"
            f"This installer will set up:\n"
            f"  • Organized folder structure\n"
            f"  • Development tools (git, kubectl, etc.)\n"
            f"  • Git config + SSH keys\n"
            f"  • Documentation server\n"
            f"  • Career tracking system\n\n"
            f"[dim]Estimated time: 10-15 minutes[/dim]",
            title="🚀 Dev Environment Setup",
            border_style="blue"
        ))
    else:
        print("\n" + "="*60)
        print("🐶 Dev Environment Setup")
        print("="*60)
        print(f"\nPlatform: {platform_name.title()} ({platform_detail})")
        print("\nThis will set up your complete dev environment.")
        print("Estimated time: 10-15 minutes\n")

# Placeholder for now - we'll build the full installer in the next iteration
def main():
    parser = argparse.ArgumentParser(description="Dev Environment Setup")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--status", action="store_true", help="Show current progress")
    parser.add_argument("--config", help="Use config file (non-interactive)")
    args = parser.parse_args()
    
    if args.status:
        show_progress()
        return
    
    # Detect platform
    platform_name, platform_detail = detect_platform()
    
    if platform_name == "unknown":
        print("❌ Unsupported platform")
        sys.exit(1)
    
    # Show banner
    print_banner(platform_name, platform_detail)
    
    # TODO: Full installer implementation
    print("\n🚧 Full installer coming in next iteration!")
    print("\nFor now, you can manually:")
    print("  1. Edit config/user-profile.yaml")
    print("  2. Run: python3 scripts/auto-deploy-docs.py")
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Publish Prism config packages to npm registry

Usage:
    python3 publish_packages.py --dry-run          # Test without publishing
    python3 publish_packages.py --package personal-dev  # Publish one package
    python3 publish_packages.py --all              # Publish all packages
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_PACKAGES_DIR = SCRIPT_DIR / "config-packages"

# Package mapping
PACKAGE_DIRS = {
    "personal-dev": "personal-dev",
    "startup": "startup-config",
    "fortune500": "fortune500-config",
    "university": "university-config",
    "consulting": "consulting-firm-config",
    "opensource": "opensource-project-config",
    "acme-corp": "acme-corp",
}


def validate_package(package_dir: Path) -> bool:
    """
    Validate package has required files.
    
    Args:
        package_dir: Path to package directory
    
    Returns:
        True if valid
    """
    required_files = ["package.json", "package.yaml"]
    
    for file in required_files:
        if not (package_dir / file).exists():
            print(f"❌ Missing {file} in {package_dir.name}")
            return False
    
    # Validate package.json
    try:
        with open(package_dir / "package.json") as f:
            pkg_json = json.load(f)
            
        if not pkg_json.get("name", "").startswith("@prism/"):
            print(f"❌ Invalid package name in {package_dir.name}")
            return False
        
        if not pkg_json.get("version"):
            print(f"❌ Missing version in {package_dir.name}")
            return False
    
    except Exception as e:
        print(f"❌ Invalid package.json in {package_dir.name}: {e}")
        return False
    
    print(f"✅ {package_dir.name} is valid")
    return True


def publish_package(package_dir: Path, dry_run: bool = False) -> bool:
    """
    Publish a package to npm.
    
    Args:
        package_dir: Path to package directory
        dry_run: If True, run npm publish --dry-run
    
    Returns:
        True if successful
    """
    if not validate_package(package_dir):
        return False
    
    # Read package.json to get name
    with open(package_dir / "package.json") as f:
        pkg_json = json.load(f)
    
    pkg_name = pkg_json["name"]
    pkg_version = pkg_json["version"]
    
    print(f"\n📦 Publishing {pkg_name}@{pkg_version}")
    
    if dry_run:
        print("  👀 DRY RUN MODE - Not actually publishing")
    
    # Build npm publish command
    cmd = ["npm", "publish", "--access", "public"]
    
    if dry_run:
        cmd.append("--dry-run")
    
    print(f"  Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=package_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ {pkg_name} published successfully!")
        if result.stdout:
            print(result.stdout)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to publish {pkg_name}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm.")
        return False


def check_npm_login() -> bool:
    """
    Check if user is logged in to npm.
    
    Returns:
        True if logged in
    """
    try:
        result = subprocess.run(
            ["npm", "whoami"],
            capture_output=True,
            text=True,
            check=True
        )
        username = result.stdout.strip()
        print(f"✅ Logged in to npm as: {username}\n")
        return True
    
    except subprocess.CalledProcessError:
        print("❌ Not logged in to npm.")
        print("\nPlease run: npm login")
        print("\nYou'll need an npm account with access to the @prism scope.")
        return False
    
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Publish Prism config packages to npm"
    )
    
    parser.add_argument(
        "--package",
        choices=list(PACKAGE_DIRS.keys()),
        help="Specific package to publish"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Publish all packages"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test publish without actually publishing"
    )
    
    args = parser.parse_args()
    
    # Check npm login (skip for dry-run)
    if not args.dry_run and not check_npm_login():
        sys.exit(1)
    
    # Determine which packages to publish
    if args.package:
        packages_to_publish = [args.package]
    elif args.all:
        packages_to_publish = list(PACKAGE_DIRS.keys())
    else:
        parser.print_help()
        sys.exit(1)
    
    # Publish packages
    print(f"\n🚀 Publishing {len(packages_to_publish)} package(s)...\n")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for pkg_key in packages_to_publish:
        pkg_dir = CONFIG_PACKAGES_DIR / PACKAGE_DIRS[pkg_key]
        
        if not pkg_dir.exists():
            print(f"❌ Package directory not found: {pkg_dir}")
            fail_count += 1
            continue
        
        if publish_package(pkg_dir, dry_run=args.dry_run):
            success_count += 1
        else:
            fail_count += 1
        
        print("=" * 60)
    
    # Summary
    print(f"\n🎯 Summary:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)
    else:
        print("\n🎉 All packages published successfully!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

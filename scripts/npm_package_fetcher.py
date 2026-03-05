#!/usr/bin/env python3
"""
NPM Package Fetcher for Prism

Fetches Prism config packages from npm registry (unpkg.com CDN)
with fallback to local packages.

Usage:
    python3 npm_package_fetcher.py list
    python3 npm_package_fetcher.py fetch @prism/personal-dev-config
    python3 npm_package_fetcher.py fetch @prism/startup-config --version 1.0.0
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
import tempfile
import shutil

# NPM registry defaults
UNPKG_BASE = "https://unpkg.com"
NPM_REGISTRY = "https://registry.npmjs.org"

# Prism package scope
PRISM_SCOPE = "@prism"

# Available packages
AVAILABLE_PACKAGES = [
    "@prism/personal-dev-config",
    "@prism/startup-config",
    "@prism/fortune500-config",
    "@prism/university-config",
    "@prism/consulting-config",
    "@prism/opensource-config",
    "@prism/acme-corp-config",
]


def fetch_package_metadata(package_name: str) -> dict:
    """
    Fetch package metadata from npm registry.
    
    Args:
        package_name: Full package name (e.g., @prism/personal-dev-config)
    
    Returns:
        Package metadata dict
    """
    url = f"{NPM_REGISTRY}/{package_name}"
    print(f"📡 Fetching metadata from npm: {package_name}")
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read())
    except urllib.error.URLError as e:
        print(f"⚠️  npm registry unavailable: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching metadata: {e}")
        return None


def fetch_package_file(package_name: str, file_path: str, version: str = "latest") -> str:
    """
    Fetch a specific file from a package via unpkg CDN.
    
    Args:
        package_name: Full package name
        file_path: Path to file within package (e.g., package.yaml)
        version: Package version (default: latest)
    
    Returns:
        File content as string
    """
    url = f"{UNPKG_BASE}/{package_name}@{version}/{file_path}"
    print(f"📥 Downloading: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"⚠️  unpkg CDN unavailable: {e}")
        return None
    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return None


def fetch_package(package_name: str, version: str = "latest", dest_dir: str = None) -> str:
    """
    Fetch entire package and extract to directory.
    
    Args:
        package_name: Full package name
        version: Package version
        dest_dir: Destination directory (default: temp dir)
    
    Returns:
        Path to extracted package directory
    """
    print(f"\n🎁 Fetching package: {package_name}@{version}")
    
    # Try npm first
    package_yaml = fetch_package_file(package_name, "package.yaml", version)
    
    if package_yaml:
        # Success! Save to destination
        if dest_dir is None:
            dest_dir = tempfile.mkdtemp(prefix="prism-pkg-")
        
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Write package.yaml
        (dest_path / "package.yaml").write_text(package_yaml)
        
        # Try to fetch other common files
        for file in ["README.md", "package.json"]:
            content = fetch_package_file(package_name, file, version)
            if content:
                (dest_path / file).write_text(content)
        
        print(f"✅ Package downloaded to: {dest_path}")
        return str(dest_path)
    
    # Fallback to local packages
    print(f"⚠️  npm unavailable, checking local packages...")
    return fetch_local_package(package_name)


def fetch_local_package(package_name: str) -> str:
    """
    Fallback: Load package from local config-packages directory.
    
    Args:
        package_name: Full package name (e.g., @prism/personal-dev-config)
    
    Returns:
        Path to local package directory
    """
    # Strip @prism/ prefix and map to local directory
    local_name = package_name.replace("@prism/", "").replace("-config", "")
    
    # Try common name variations
    variations = [
        local_name,
        local_name + "-config",
        local_name.replace("-", "_"),
    ]
    
    script_dir = Path(__file__).parent.parent
    config_packages_dir = script_dir / "config-packages"
    
    for variant in variations:
        local_path = config_packages_dir / variant
        if local_path.exists() and (local_path / "package.yaml").exists():
            print(f"✅ Using local package: {local_path}")
            return str(local_path)
    
    print(f"❌ Package not found: {package_name}")
    print(f"   Looked in: {config_packages_dir}")
    print(f"   Tried: {variations}")
    return None


def list_available_packages(use_npm: bool = True) -> list:
    """
    List all available Prism config packages.
    
    Args:
        use_npm: Try to fetch from npm registry (default: True)
    
    Returns:
        List of package dicts with metadata
    """
    packages = []
    
    if use_npm:
        print("\n📦 Available Prism Config Packages (from npm):")
        print("=" * 60)
        
        for pkg_name in AVAILABLE_PACKAGES:
            metadata = fetch_package_metadata(pkg_name)
            if metadata:
                latest_version = metadata.get("dist-tags", {}).get("latest", "unknown")
                description = metadata.get("description", "No description")
                packages.append({
                    "name": pkg_name,
                    "version": latest_version,
                    "description": description,
                    "source": "npm"
                })
                print(f"\n  {pkg_name}")
                print(f"    Version: {latest_version}")
                print(f"    {description}")
            else:
                # Fallback to local
                local_path = fetch_local_package(pkg_name)
                if local_path:
                    packages.append({
                        "name": pkg_name,
                        "version": "local",
                        "description": "Local package",
                        "source": "local",
                        "path": local_path
                    })
    
    else:
        # Local only
        print("\n📦 Available Prism Config Packages (local):")
        print("=" * 60)
        
        for pkg_name in AVAILABLE_PACKAGES:
            local_path = fetch_local_package(pkg_name)
            if local_path:
                packages.append({
                    "name": pkg_name,
                    "version": "local",
                    "source": "local",
                    "path": local_path
                })
                print(f"\n  {pkg_name}")
                print(f"    Path: {local_path}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(packages)} packages\n")
    
    return packages


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Prism config packages from npm or local directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available packages")
    list_parser.add_argument(
        "--local",
        action="store_true",
        help="Only show local packages"
    )
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a package")
    fetch_parser.add_argument("package", help="Package name (e.g., @prism/personal-dev-config)")
    fetch_parser.add_argument("--version", default="latest", help="Package version")
    fetch_parser.add_argument("--dest", help="Destination directory")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_available_packages(use_npm=not args.local)
    
    elif args.command == "fetch":
        result = fetch_package(args.package, args.version, args.dest)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

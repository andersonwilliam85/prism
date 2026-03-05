#!/usr/bin/env python3
"""
Config Package Manager

Installs company/org/dept/team configuration packages.

Usage:
    python3 scripts/package_manager.py install walmart-config
    python3 scripts/package_manager.py list
    python3 scripts/package_manager.py search <query>
"""

import yaml
import argparse
import shutil
from pathlib import Path
import requests
import subprocess
from typing import Dict, Optional


class PackageManager:
    """Manages config package installation"""
    
    def __init__(self, root_dir: Path = None):
        """Initialize package manager"""
        self.root_dir = root_dir or Path.cwd()
        self.packages_dir = self.root_dir / "config-packages"
        self.config_dir = self.root_dir / "config"
    
    def list_packages(self) -> list:
        """List all available config packages"""
        packages = []
        
        # Scan local packages
        if self.packages_dir.exists():
            for pkg_dir in self.packages_dir.iterdir():
                if pkg_dir.is_dir():
                    package_yaml = pkg_dir / "package.yaml"
                    if package_yaml.exists():
                        with open(package_yaml) as f:
                            metadata = yaml.safe_load(f)
                            packages.append({
                                "name": metadata["package"]["name"],
                                "version": metadata["package"]["version"],
                                "description": metadata["package"]["description"],
                                "type": metadata["package"]["type"],
                                "source": "local",
                                "path": str(pkg_dir)
                            })
        
        return packages
    
    def install_package(self, package_name: str, source: str = None) -> bool:
        """
        Install a config package
        
        Args:
            package_name: Name of package (e.g., "walmart-config")
            source: Optional source (local path, git url, or registry)
        
        Returns:
            True if successful
        """
        print(f"\n📦 Installing {package_name}...")
        
        # Find package
        package_dir = self._find_package(package_name, source)
        if not package_dir:
            print(f"❌ Package not found: {package_name}")
            return False
        
        # Load metadata
        metadata_path = package_dir / "package.yaml"
        with open(metadata_path) as f:
            metadata = yaml.safe_load(f)
        
        # Install files
        install_config = metadata["package"]["install"]
        
        print(f"  ⚙️  Installing files...")
        
        # Copy files
        for file_spec in install_config.get("files", []):
            source_file = package_dir / file_spec["source"]
            dest_file = self.root_dir / file_spec["dest"]
            
            # Create parent dirs
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy
            shutil.copy2(source_file, dest_file)
            print(f"    ✅ {file_spec['dest']}")
        
        # Copy directories
        for dir_spec in install_config.get("directories", []):
            source_dir = package_dir / dir_spec["source"]
            dest_dir = self.root_dir / dir_spec["dest"]
            
            if source_dir.exists():
                # Create dest
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy all files in dir
                for item in source_dir.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(source_dir)
                        dest_file = dest_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_file)
                
                print(f"    ✅ {dir_spec['dest']} (directory)")
        
        # Post-install script
        post_install = metadata["package"].get("post_install", {})
        if "script" in post_install:
            script_path = package_dir / post_install["script"]
            if script_path.exists():
                print(f"  ⚙️  Running post-install script...")
                subprocess.run(["bash", str(script_path)], cwd=self.root_dir)
        
        # Show message
        if "message" in post_install:
            print(f"\n🎉 {post_install['message']}")
        
        print(f"\n✅ {package_name} installed successfully!\n")
        return True
    
    def _find_package(self, package_name: str, source: str = None) -> Optional[Path]:
        """Find package directory"""
        # Local package
        local_path = self.packages_dir / package_name.replace("-config", "")
        if local_path.exists():
            return local_path
        
        # Custom source
        if source:
            # TODO: Handle git URLs, registry URLs
            source_path = Path(source)
            if source_path.exists():
                return source_path
        
        return None


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Config Package Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # list command
    subparsers.add_parser("list", help="List available packages")
    
    # install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package name")
    install_parser.add_argument("--source", help="Package source (optional)")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search packages")
    search_parser.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    
    pm = PackageManager()
    
    if args.command == "list":
        packages = pm.list_packages()
        print("\n📦 Available Config Packages:\n")
        for pkg in packages:
            print(f"  • {pkg['name']} (v{pkg['version']}) - {pkg['description']}")
            print(f"    Type: {pkg['type']} | Source: {pkg['source']}")
            print()
    
    elif args.command == "install":
        pm.install_package(args.package, args.source)
    
    elif args.command == "search":
        packages = pm.list_packages()
        results = [p for p in packages if args.query.lower() in p['name'].lower() or args.query.lower() in p['description'].lower()]
        
        print(f"\n🔍 Search results for '{args.query}':\n")
        for pkg in results:
            print(f"  • {pkg['name']} - {pkg['description']}")
        print()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

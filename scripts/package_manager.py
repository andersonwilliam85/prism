#!/usr/bin/env python3
"""
Config Package Manager

Manages config packages (install, list, search, info, validate).
Auto-discovers packages in config-packages/ directory.

Usage:
    python3 scripts/package_manager.py list
    python3 scripts/package_manager.py search <query>
    python3 scripts/package_manager.py info <package-name>
    python3 scripts/package_manager.py install <package-name>
    python3 scripts/package_manager.py validate <package-name>
    python3 scripts/package_manager.py create <new-package-name>
"""

import yaml
import argparse
import shutil
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PackageManager:
    """Manages config package installation"""
    
    def __init__(self, root_dir: Path = None):
        """Initialize package manager"""
        self.root_dir = root_dir or Path.cwd()
        self.packages_dir = self.root_dir / "config-packages"
        self.config_dir = self.root_dir / "config"
    
    def discover_packages(self) -> List[Dict]:
        """
        Auto-discover all packages in config-packages/ directory
        
        Returns:
            List of package metadata dicts
        """
        packages = []
        
        if not self.packages_dir.exists():
            return packages
        
        # Scan all subdirectories
        for pkg_dir in self.packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            
            # Look for package.yaml
            package_yaml = pkg_dir / "package.yaml"
            if not package_yaml.exists():
                continue
            
            try:
                with open(package_yaml) as f:
                    metadata = yaml.safe_load(f)
                    
                    # Check if discoverable
                    dist = metadata.get("distribution", {})
                    if not dist.get("local", {}).get("discoverable", True):
                        continue
                    
                    pkg_info = metadata["package"]
                    packages.append({
                        "name": pkg_info["name"],
                        "version": pkg_info["version"],
                        "description": pkg_info["description"],
                        "type": pkg_info["type"],
                        "author": pkg_info.get("author", "Unknown"),
                        "source": "local",
                        "path": str(pkg_dir),
                        "tags": metadata.get("metadata", {}).get("tags", []),
                        "company_size": metadata.get("metadata", {}).get("company_size", "unknown")
                    })
            except Exception as e:
                print(f"  ⚠️  Warning: Could not load {pkg_dir.name}: {e}")
                continue
        
        return packages
    
    def list_packages(self) -> List[Dict]:
        """List all available config packages (wrapper for discover)"""
        return self.discover_packages()
    
    def install_package(self, package_name: str, source: str = None) -> bool:
        """
        Install a config package
        
        Args:
            package_name: Name of package (e.g., "fortune500-config")
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
    
    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """
        Get detailed info about a package
        
        Args:
            package_name: Name of package
        
        Returns:
            Full package metadata dict or None
        """
        pkg_dir = self._find_package(package_name)
        if not pkg_dir:
            return None
        
        package_yaml = pkg_dir / "package.yaml"
        if not package_yaml.exists():
            return None
        
        with open(package_yaml) as f:
            return yaml.safe_load(f)
    
    def validate_package(self, package_name: str) -> tuple[bool, List[str]]:
        """
        Validate a package structure and metadata
        
        Args:
            package_name: Name of package to validate
        
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Find package
        pkg_dir = self._find_package(package_name)
        if not pkg_dir:
            return False, [f"Package not found: {package_name}"]
        
        # Check package.yaml exists
        package_yaml = pkg_dir / "package.yaml"
        if not package_yaml.exists():
            errors.append("Missing package.yaml")
            return False, errors
        
        # Load and validate metadata
        try:
            with open(package_yaml) as f:
                metadata = yaml.safe_load(f)
        except Exception as e:
            errors.append(f"Invalid YAML in package.yaml: {e}")
            return False, errors
        
        # Validate required fields
        pkg_info = metadata.get("package", {})
        required_fields = ["name", "version", "description", "type"]
        for field in required_fields:
            if field not in pkg_info:
                errors.append(f"Missing required field: package.{field}")
        
        # Validate install config
        install_config = pkg_info.get("install", {})
        if not install_config:
            errors.append("Missing install configuration")
        
        # Check that source files exist
        for file_spec in install_config.get("files", []):
            source_file = pkg_dir / file_spec["source"]
            if not source_file.exists():
                errors.append(f"Source file not found: {file_spec['source']}")
        
        for dir_spec in install_config.get("directories", []):
            source_dir = pkg_dir / dir_spec["source"]
            if not source_dir.exists():
                errors.append(f"Source directory not found: {dir_spec['source']}")
        
        return len(errors) == 0, errors
    
    def create_package_scaffold(self, package_name: str, company_name: str = None) -> bool:
        """
        Create a new package scaffold from template
        
        Args:
            package_name: Name for new package (e.g., "mycompany-config")
            company_name: Display name (e.g., "My Company")
        
        Returns:
            True if successful
        """
        # Derive company name if not provided
        if not company_name:
            company_name = package_name.replace("-config", "").replace("-", " ").title()
        
        pkg_dir = self.packages_dir / package_name.replace("-config", "")
        
        if pkg_dir.exists():
            print(f"❌ Package directory already exists: {pkg_dir}")
            return False
        
        print(f"\n🏭 Creating package scaffold for {company_name}...")
        
        # Create directory structure
        (pkg_dir / "base").mkdir(parents=True)
        (pkg_dir / "orgs").mkdir(parents=True)
        (pkg_dir / "teams").mkdir(parents=True)
        
        # Create package.yaml
        package_yaml_content = f"""# Package metadata
package:
  name: "{package_name}"
  version: "1.0.0"
  description: "{company_name} development environment configuration"
  author: "{company_name} IT Team"
  homepage: "https://dev.example.com"
  type: "company"
  
  requires:
    onboarding_version: ">=1.0.0"
  
  install:
    target_dir: "config/"
    files:
      - source: "welcome.yaml"
        dest: "config/welcome.yaml"
      - source: "resources.yaml"
        dest: "config/resources.yaml"
    directories:
      - source: "base/"
        dest: "config/base/"
      - source: "orgs/"
        dest: "config/orgs/"
      - source: "teams/"
        dest: "config/teams/"
  
  post_install:
    message: |
      🎉 {company_name} config installed!
      Edit config/inheritance.yaml to customize.

contents:
  base_config: "base/{package_name.replace('-config', '')}.yaml"
  welcome_page: "welcome.yaml"
  resources: "resources.yaml"

distribution:
  local:
    path: "config-packages/{package_name.replace('-config', '')}/"
    discoverable: true

metadata:
  tags: ["company", "template"]
  last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
"""
        (pkg_dir / "package.yaml").write_text(package_yaml_content)
        print(f"  ✅ Created package.yaml")
        
        # Create minimal base config
        base_config = f"""company:
  name: "{company_name}"
  domain: "example.com"

environment:
  proxy:
    http: "http://proxy.example.com:8080"
    https: "http://proxy.example.com:8080"

git:
  user:
    name: "${{USER}}"
    email: "${{USER}}@example.com"

tools_required:
  - git
  - docker
"""
        base_file = pkg_dir / "base" / f"{package_name.replace('-config', '')}.yaml"
        base_file.write_text(base_config)
        print(f"  ✅ Created {base_file.name}")
        
        # Create minimal welcome.yaml
        welcome_content = f"""company:
  name: "{company_name}"

welcome:
  title: "Welcome to {company_name}"
  subtitle: "Your development environment is ready!"

branding:
  footer_text: "Built by {company_name}"
"""
        (pkg_dir / "welcome.yaml").write_text(welcome_content)
        print(f"  ✅ Created welcome.yaml")
        
        # Create minimal resources.yaml
        resources_content = f"""company:
  name: "{company_name}"

resources:
  developer_tools:
    - name: "GitHub"
      url: "https://github.com"
      description: "Source code"
"""
        (pkg_dir / "resources.yaml").write_text(resources_content)
        print(f"  ✅ Created resources.yaml")
        
        # Create README
        readme_content = f"""# {company_name} Config Package

**Version:** 1.0.0

Development environment configuration for {company_name}.

## Installation

```bash
python3 scripts/package_manager.py install {package_name}
```

## Customization

Edit the files in this directory to customize for your company:

- `base/*.yaml` - Company-wide settings
- `orgs/*.yaml` - Add your sub-organizations
- `teams/*.yaml` - Add your teams
- `welcome.yaml` - Customize welcome page
- `resources.yaml` - Add your internal links
"""
        (pkg_dir / "README.md").write_text(readme_content)
        print(f"  ✅ Created README.md")
        
        print(f"\n✅ Package scaffold created at: {pkg_dir}")
        print(f"\nNext steps:")
        print(f"  1. Edit {pkg_dir}/package.yaml")
        print(f"  2. Customize configs in {pkg_dir}/base/")
        print(f"  3. Add your orgs/teams")
        print(f"  4. Test: python3 scripts/package_manager.py validate {package_name}")
        print(f"  5. Install: python3 scripts/package_manager.py install {package_name}")
        
        return True
    
    def _find_package(self, package_name: str, source: str = None) -> Optional[Path]:
        """Find package directory"""
        # Try exact match first
        for pkg in self.discover_packages():
            if pkg["name"] == package_name:
                return Path(pkg["path"])
        
        # Try directory name match (without -config suffix)
        local_path = self.packages_dir / package_name.replace("-config", "")
        if local_path.exists():
            return local_path
        
        # Custom source
        if source:
            source_path = Path(source)
            if source_path.exists():
                return source_path
        
        return None


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Config Package Manager - Manage dev onboarding config packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/package_manager.py list
  python3 scripts/package_manager.py info fortune500-config
  python3 scripts/package_manager.py install fortune500-config
  python3 scripts/package_manager.py validate fortune500-config
  python3 scripts/package_manager.py create mycompany-config
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # list command
    subparsers.add_parser("list", help="List all available packages")
    
    # info command
    info_parser = subparsers.add_parser("info", help="Show detailed package info")
    info_parser.add_argument("package", help="Package name")
    
    # install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package name")
    install_parser.add_argument("--source", help="Package source (optional)")
    install_parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate package structure")
    validate_parser.add_argument("package", help="Package name")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search packages")
    search_parser.add_argument("query", help="Search query")
    
    # create command
    create_parser = subparsers.add_parser("create", help="Create new package scaffold")
    create_parser.add_argument("package", help="Package name (e.g., mycompany-config)")
    create_parser.add_argument("--company", help="Company display name (optional)")
    
    args = parser.parse_args()
    
    pm = PackageManager()
    
    # Commands
    if args.command == "list":
        packages = pm.list_packages()
        print("\n📦 Available Config Packages\n")
        print("="*70)
        
        if not packages:
            print("  No packages found in config-packages/")
            print("\n  Create one with: python3 scripts/package_manager.py create <name>")
        else:
            for pkg in packages:
                print(f"\n  📦 {pkg['name']} (v{pkg['version']})")
                print(f"     {pkg['description']}")
                print(f"     Type: {pkg['type']} | Size: {pkg['company_size']} | Author: {pkg['author']}")
                if pkg['tags']:
                    print(f"     Tags: {', '.join(pkg['tags'])}")
        
        print("\n" + "="*70)
        print(f"  Total: {len(packages)} package(s)\n")
    
    elif args.command == "info":
        info = pm.get_package_info(args.package)
        if not info:
            print(f"❌ Package not found: {args.package}")
            return
        
        pkg_info = info["package"]
        contents = info.get("contents", {})
        metadata = info.get("metadata", {})
        
        print(f"\n📦 Package Info: {pkg_info['name']}")
        print("="*70)
        print(f"  Version:      {pkg_info['version']}")
        print(f"  Type:         {pkg_info['type']}")
        print(f"  Author:       {pkg_info.get('author', 'Unknown')}")
        print(f"  Homepage:     {pkg_info.get('homepage', 'N/A')}")
        print(f"  Description:  {pkg_info['description']}")
        
        # Support
        if "support" in pkg_info:
            print(f"\n  🆘 Support:")
            for key, val in pkg_info["support"].items():
                print(f"     {key}: {val}")
        
        # Contents
        if "sub_orgs" in contents:
            print(f"\n  🏢 Sub-Organizations: {len(contents['sub_orgs'])}")
            for org in contents["sub_orgs"]:
                if isinstance(org, dict):
                    print(f"     - {org['name']} ({org['id']})")
                else:
                    print(f"     - {org}")
        
        if "departments" in contents:
            print(f"\n  🏪 Departments: {len(contents['departments'])}")
            for dept in contents["departments"]:
                if isinstance(dept, dict):
                    print(f"     - {dept['name']} ({dept['id']})")
                else:
                    print(f"     - {dept}")
        
        if "teams" in contents:
            print(f"\n  👥 Teams: {len(contents['teams'])}")
            for team in contents["teams"]:
                if isinstance(team, dict):
                    print(f"     - {team['name']} ({team['id']})")
                else:
                    print(f"     - {team}")
        
        # Metadata
        if metadata:
            print(f"\n  🏷️  Metadata:")
            if "tags" in metadata:
                print(f"     Tags: {', '.join(metadata['tags'])}")
            if "company_size" in metadata:
                print(f"     Company Size: {metadata['company_size']}")
            if "last_updated" in metadata:
                print(f"     Last Updated: {metadata['last_updated']}")
        
        print("\n" + "="*70 + "\n")
    
    elif args.command == "install":
        if args.dry_run:
            print(f"\n[DRY RUN] Would install: {args.package}")
            # Show what would be copied
            info = pm.get_package_info(args.package)
            if info:
                install_config = info["package"]["install"]
                print("\nFiles to install:")
                for f in install_config.get("files", []):
                    print(f"  - {f['dest']}")
                for d in install_config.get("directories", []):
                    print(f"  - {d['dest']} (directory)")
            print()
        else:
            pm.install_package(args.package, args.source)
    
    elif args.command == "validate":
        print(f"\n🔍 Validating package: {args.package}...\n")
        is_valid, errors = pm.validate_package(args.package)
        
        if is_valid:
            print("✅ Package is valid!\n")
        else:
            print("❌ Package has errors:\n")
            for error in errors:
                print(f"  - {error}")
            print()
    
    elif args.command == "search":
        packages = pm.list_packages()
        query_lower = args.query.lower()
        results = [
            p for p in packages 
            if query_lower in p['name'].lower() 
            or query_lower in p['description'].lower()
            or query_lower in ' '.join(p['tags']).lower()
        ]
        
        print(f"\n🔍 Search results for '{args.query}'\n")
        print("="*70)
        
        if not results:
            print("  No packages found matching query.")
        else:
            for pkg in results:
                print(f"\n  • {pkg['name']} - {pkg['description']}")
                if pkg['tags']:
                    print(f"    Tags: {', '.join(pkg['tags'])}")
        
        print("\n" + "="*70)
        print(f"  Found: {len(results)} package(s)\n")
    
    elif args.command == "create":
        pm.create_package_scaffold(args.package, args.company)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

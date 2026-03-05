#!/usr/bin/env python3
"""
Package Validator

Validates config packages to ensure they have required fields and structure.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any


class PackageValidator:
    """Validates config packages"""
    
    REQUIRED_PACKAGE_FIELDS = [
        'name',
        'version',
        'description'
    ]
    
    REQUIRED_TOP_LEVEL_KEYS = [
        'package'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_package(self, package_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a package directory
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check if directory exists
        if not package_path.exists():
            self.errors.append(f"Package directory does not exist: {package_path}")
            return False, self.errors, self.warnings
        
        if not package_path.is_dir():
            self.errors.append(f"Package path is not a directory: {package_path}")
            return False, self.errors, self.warnings
        
        # Check for package.yaml
        package_yaml = package_path / 'package.yaml'
        if not package_yaml.exists():
            self.errors.append("Missing required file: package.yaml")
            return False, self.errors, self.warnings
        
        # Try to parse YAML
        try:
            with open(package_yaml) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Failed to read package.yaml: {e}")
            return False, self.errors, self.warnings
        
        if not config:
            self.errors.append("package.yaml is empty")
            return False, self.errors, self.warnings
        
        # Validate top-level structure
        for key in self.REQUIRED_TOP_LEVEL_KEYS:
            if key not in config:
                self.errors.append(f"Missing required top-level key: '{key}'")
        
        # Validate package section
        if 'package' in config:
            package_section = config['package']
            if not isinstance(package_section, dict):
                self.errors.append("'package' must be a dictionary")
            else:
                for field in self.REQUIRED_PACKAGE_FIELDS:
                    if field not in package_section:
                        self.errors.append(f"Missing required package field: '{field}'")
                    elif not package_section[field]:
                        self.errors.append(f"Empty required package field: '{field}'")
        
        # Validate user_info_fields if present
        user_fields = config.get('user_info_fields', config.get('package', {}).get('user_info_fields', []))
        if user_fields:
            if not isinstance(user_fields, list):
                self.errors.append("'user_info_fields' must be a list")
            else:
                for idx, field in enumerate(user_fields):
                    if not isinstance(field, dict):
                        self.errors.append(f"user_info_fields[{idx}] must be a dictionary")
                        continue
                    
                    if 'id' not in field:
                        self.errors.append(f"user_info_fields[{idx}] missing required 'id' field")
                    if 'label' not in field:
                        self.errors.append(f"user_info_fields[{idx}] missing required 'label' field")
                    if 'type' not in field:
                        self.errors.append(f"user_info_fields[{idx}] missing required 'type' field")
        else:
            self.warnings.append("No user_info_fields defined - will use defaults")
        
        # Check for README (optional but recommended)
        if not (package_path / 'README.md').exists():
            self.warnings.append("No README.md found (recommended)")
        
        # Validate metadata if present
        if 'metadata' in config:
            metadata = config['metadata']
            if not isinstance(metadata, dict):
                self.errors.append("'metadata' must be a dictionary")
            else:
                if 'tags' in metadata and not isinstance(metadata['tags'], list):
                    self.errors.append("'metadata.tags' must be a list")
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def get_package_info(self, package_path: Path) -> Dict[str, Any]:
        """
        Extract basic package info (even if invalid)
        
        Returns:
            Dict with name, version, description, or error info
        """
        try:
            package_yaml = package_path / 'package.yaml'
            if not package_yaml.exists():
                return {
                    'id': package_path.name,
                    'name': package_path.name,
                    'version': 'unknown',
                    'description': 'No package.yaml found',
                    'error': True
                }
            
            with open(package_yaml) as f:
                config = yaml.safe_load(f)
            
            if not config:
                return {
                    'id': package_path.name,
                    'name': package_path.name,
                    'version': 'unknown',
                    'description': 'Empty package.yaml',
                    'error': True
                }
            
            package_info = config.get('package', {})
            
            return {
                'id': package_path.name,
                'name': package_info.get('name', package_path.name),
                'version': package_info.get('version', 'unknown'),
                'description': package_info.get('description', 'No description'),
                'error': False
            }
        except Exception as e:
            return {
                'id': package_path.name,
                'name': package_path.name,
                'version': 'unknown',
                'description': f'Error: {str(e)}',
                'error': True
            }


def validate_all_packages(packages_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate all packages in a directory
    
    Returns:
        (valid_packages, invalid_packages)
    """
    validator = PackageValidator()
    valid_packages = []
    invalid_packages = []
    
    if not packages_dir.exists():
        return [], []
    
    for package_path in packages_dir.iterdir():
        if not package_path.is_dir():
            continue
        
        if package_path.name.startswith('.'):
            continue
        
        is_valid, errors, warnings = validator.validate_package(package_path)
        info = validator.get_package_info(package_path)
        
        package_data = {
            **info,
            'path': str(package_path),
            'errors': errors,
            'warnings': warnings
        }
        
        if is_valid:
            valid_packages.append(package_data)
        else:
            invalid_packages.append(package_data)
    
    return valid_packages, invalid_packages


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    # Test validation
    if len(sys.argv) > 1:
        package_path = Path(sys.argv[1])
    else:
        package_path = Path(__file__).parent.parent / 'config-packages'
    
    if package_path.is_dir() and (package_path / 'package.yaml').exists():
        # Validate single package
        validator = PackageValidator()
        is_valid, errors, warnings = validator.validate_package(package_path)
        
        print(f"\n📦 Validating: {package_path.name}")
        print(f"\nValid: {is_valid}")
        
        if errors:
            print("\n❌ Errors:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
    else:
        # Validate all packages
        valid, invalid = validate_all_packages(package_path)
        
        print(f"\n📊 Package Validation Results\n")
        print(f"✅ Valid: {len(valid)}")
        print(f"❌ Invalid: {len(invalid)}")
        
        if valid:
            print("\n✅ Valid Packages:")
            for pkg in valid:
                warnings_text = f" ({len(pkg['warnings'])} warnings)" if pkg['warnings'] else ""
                print(f"  - {pkg['name']}{warnings_text}")
        
        if invalid:
            print("\n❌ Invalid Packages:")
            for pkg in invalid:
                print(f"\n  {pkg['name']}:")
                for error in pkg['errors']:
                    print(f"    - {error}")

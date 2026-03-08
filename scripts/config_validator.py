#!/usr/bin/env python3
"""
Configuration Validator

Validates loaded configuration content for correctness and completeness.
Provides high-level error messages for debugging.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


class ConfigValidator:
    """Validates configuration files"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.context = ""

    def validate_config_file(self, config_path: Path, config_type: str = "config") -> Tuple[bool, List[str], List[str]]:
        """
        Validate a single configuration file

        Args:
            config_path: Path to config file
            config_type: Type of config (base, org, department, team, user)

        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.context = f"{config_type}: {config_path.name}"

        # Check file exists
        if not config_path.exists():
            self.errors.append(f"Configuration file not found: {config_path.name}")
            return False, self.errors, self.warnings

        # Try to parse YAML
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax in {config_path.name}: {str(e)[:100]}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Failed to read {config_path.name}: {str(e)[:100]}")
            return False, self.errors, self.warnings

        if not config:
            self.errors.append(f"Configuration file is empty: {config_path.name}")
            return False, self.errors, self.warnings

        if not isinstance(config, dict):
            self.errors.append(f"Configuration must be a dictionary, got {type(config).__name__}")
            return False, self.errors, self.warnings

        # Validate based on type
        if config_type in ["base", "company"]:
            self._validate_base_config(config)
        elif config_type == "org":
            self._validate_org_config(config)
        elif config_type == "department":
            self._validate_department_config(config)
        elif config_type == "team":
            self._validate_team_config(config)
        elif config_type == "user":
            self._validate_user_config(config)

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_base_config(self, config: Dict[str, Any]) -> None:
        """Validate base/company configuration"""

        # Check for company section
        if "company" not in config:
            self.errors.append("Missing required 'company' section")
            return

        company = config["company"]
        if not isinstance(company, dict):
            self.errors.append("'company' must be a dictionary")
            return

        # Required company fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in company:
                self.errors.append(f"Missing required company field: '{field}'")
            elif not company[field]:
                self.errors.append(f"Company field '{field}' cannot be empty")

        # Validate git config if present
        if "git" in config:
            self._validate_git_config(config["git"])

        # Validate environment if present
        if "environment" in config:
            self._validate_environment_config(config["environment"])

    def _validate_org_config(self, config: Dict[str, Any]) -> None:
        """Validate organization configuration"""

        if "organization" not in config and "org" not in config:
            self.errors.append("Missing 'organization' or 'org' section")
            return

        org = config.get("organization", config.get("org", {}))
        if not isinstance(org, dict):
            self.errors.append("Organization section must be a dictionary")
            return

        if "name" not in org:
            self.errors.append("Organization missing required 'name' field")
        elif not org["name"]:
            self.errors.append("Organization name cannot be empty")

    def _validate_department_config(self, config: Dict[str, Any]) -> None:
        """Validate department configuration"""

        if "department" not in config and "dept" not in config:
            self.errors.append("Missing 'department' or 'dept' section")
            return

        dept = config.get("department", config.get("dept", {}))
        if not isinstance(dept, dict):
            self.errors.append("Department section must be a dictionary")
            return

        if "name" not in dept:
            self.errors.append("Department missing required 'name' field")
        elif not dept["name"]:
            self.errors.append("Department name cannot be empty")

    def _validate_team_config(self, config: Dict[str, Any]) -> None:
        """Validate team configuration"""

        if "team" not in config:
            self.errors.append("Missing 'team' section")
            return

        team = config["team"]
        if not isinstance(team, dict):
            self.errors.append("Team section must be a dictionary")
            return

        if "name" not in team:
            self.errors.append("Team missing required 'name' field")
        elif not team["name"]:
            self.errors.append("Team name cannot be empty")

    def _validate_user_config(self, config: Dict[str, Any]) -> None:
        """Validate user configuration"""

        if "user" not in config:
            self.warnings.append("No 'user' section found (optional)")
            return

        user = config["user"]
        if not isinstance(user, dict):
            self.errors.append("User section must be a dictionary")
            return

        # Common user fields to check
        recommended_fields = ["name", "email"]
        for field in recommended_fields:
            if field not in user:
                self.warnings.append(f"User missing recommended field: '{field}'")

    def _validate_git_config(self, git_config: Any) -> None:
        """Validate git configuration section"""

        if not isinstance(git_config, dict):
            self.errors.append("'git' section must be a dictionary")
            return

        # Check for invalid URL formats
        if "url" in git_config:
            url = git_config["url"]
            if url and not (url.startswith("http://") or url.startswith("https://") or url.startswith("git@")):
                self.errors.append(f"Invalid git URL format: {url}")

        # Validate enterprise config
        if "enterprise" in git_config:
            enterprise = git_config["enterprise"]
            if isinstance(enterprise, dict):
                if "enterprise_url" in enterprise:
                    url = enterprise["enterprise_url"]
                    if url and not (url.startswith("http://") or url.startswith("https://")):
                        self.errors.append(f"Invalid GitHub Enterprise URL: {url}")

    def _validate_environment_config(self, env_config: Any) -> None:
        """Validate environment configuration section"""

        if not isinstance(env_config, dict):
            self.errors.append("'environment' section must be a dictionary")
            return

        # Validate proxy if present
        if "proxy" in env_config:
            proxy = env_config["proxy"]
            if isinstance(proxy, dict):
                for key in ["http", "https"]:
                    if key in proxy:
                        proxy_url = proxy[key]
                        if proxy_url and not (proxy_url.startswith("http://") or proxy_url.startswith("https://")):
                            self.errors.append(f"Invalid {key} proxy URL: {proxy_url}")


class PackageConfigValidator:
    """Validates entire package configuration set"""

    def __init__(self, package_path: Path):
        self.package_path = package_path
        self.validator = ConfigValidator()
        self.all_errors = []
        self.all_warnings = []

    def validate_package_configs(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate all configuration files in a package

        Returns:
            (is_valid, validation_results)

            validation_results is a list of dicts:
            {
                'file': 'base/company.yaml',
                'type': 'base',
                'valid': True/False,
                'errors': [...],
                'warnings': [...]
            }
        """
        results = []

        # Validate base configs
        base_dir = self.package_path / "base"
        if base_dir.exists():
            for config_file in base_dir.glob("*.yaml"):
                is_valid, errors, warnings = self.validator.validate_config_file(config_file, "base")
                results.append(
                    {
                        "file": f"base/{config_file.name}",
                        "type": "base",
                        "valid": is_valid,
                        "errors": errors,
                        "warnings": warnings,
                    }
                )

        # Validate org configs
        orgs_dir = self.package_path / "orgs"
        if orgs_dir.exists():
            for config_file in orgs_dir.glob("*.yaml"):
                is_valid, errors, warnings = self.validator.validate_config_file(config_file, "org")
                results.append(
                    {
                        "file": f"orgs/{config_file.name}",
                        "type": "org",
                        "valid": is_valid,
                        "errors": errors,
                        "warnings": warnings,
                    }
                )

        # Validate department configs
        depts_dir = self.package_path / "departments"
        if depts_dir.exists():
            for config_file in depts_dir.glob("*.yaml"):
                is_valid, errors, warnings = self.validator.validate_config_file(config_file, "department")
                results.append(
                    {
                        "file": f"departments/{config_file.name}",
                        "type": "department",
                        "valid": is_valid,
                        "errors": errors,
                        "warnings": warnings,
                    }
                )

        # Validate team configs
        teams_dir = self.package_path / "teams"
        if teams_dir.exists():
            for config_file in teams_dir.glob("*.yaml"):
                is_valid, errors, warnings = self.validator.validate_config_file(config_file, "team")
                results.append(
                    {
                        "file": f"teams/{config_file.name}",
                        "type": "team",
                        "valid": is_valid,
                        "errors": errors,
                        "warnings": warnings,
                    }
                )

        # Overall validity
        all_valid = all(r["valid"] for r in results)

        return all_valid, results

    def get_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get high-level summary of validation results

        Returns:
            {
                'valid': True/False,
                'total_files': 10,
                'valid_files': 8,
                'invalid_files': 2,
                'total_errors': 5,
                'total_warnings': 3,
                'error_summary': ['Missing company name', ...]
            }
        """
        total_files = len(results)
        valid_files = sum(1 for r in results if r["valid"])
        invalid_files = total_files - valid_files

        all_errors = []
        all_warnings = []

        for result in results:
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])

        # Create summary of unique error types
        error_summary = list(set([e.split(":")[0] for e in all_errors[:10]]))  # First 10 unique error types

        return {
            "valid": invalid_files == 0,
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "error_summary": error_summary,
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 config_validator.py <package_path>")
        sys.exit(1)

    package_path = Path(sys.argv[1])

    if not package_path.exists():
        print(f"Error: Package not found: {package_path}")
        sys.exit(1)

    print(f"\n🔍 Validating configurations in: {package_path.name}\n")

    pcv = PackageConfigValidator(package_path)
    all_valid, results = pcv.validate_package_configs()
    summary = pcv.get_summary(results)

    # Print summary
    print("📊 Validation Summary:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  ✅ Valid: {summary['valid_files']}")
    print(f"  ❌ Invalid: {summary['invalid_files']}")
    print(f"  Errors: {summary['total_errors']}")
    print(f"  Warnings: {summary['total_warnings']}")
    print()

    # Print detailed results
    if not all_valid:
        print("❌ Configuration Validation Failed\n")
        for result in results:
            if not result["valid"]:
                print(f"  {result['file']}:")
                for error in result["errors"]:
                    print(f"    ❌ {error}")
                if result["warnings"]:
                    for warning in result["warnings"]:
                        print(f"    ⚠️  {warning}")
                print()
    else:
        print("✅ All configurations are valid!\n")

        # Show warnings if any
        if summary["total_warnings"] > 0:
            print("⚠️  Warnings:\n")
            for result in results:
                if result["warnings"]:
                    print(f"  {result['file']}:")
                    for warning in result["warnings"]:
                        print(f"    ⚠️  {warning}")
                    print()

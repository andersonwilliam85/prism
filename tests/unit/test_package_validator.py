"""
Unit tests for package validator.
"""
import pytest
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from package_validator import PackageValidator, validate_all_packages


@pytest.mark.unit
class TestPackageValidator:
    """Test package validation logic."""
    
    def test_validates_valid_package(self, test_package_dir):
        """Test validation of a valid package."""
        validator = PackageValidator()
        result, errors = validator.validate_package(test_package_dir)
        
        assert result is True
        assert len(errors) == 0
    
    def test_detects_missing_package_yaml(self, temp_dir):
        """Test detection of missing package.yaml."""
        validator = PackageValidator()
        result, errors = validator.validate_package(temp_dir)
        
        assert result is False
        assert any("package.yaml" in error for error in errors)
    
    def test_detects_missing_required_field(self, test_package_dir):
        """Test detection of missing required fields."""
        # Create invalid package
        pkg_yaml = test_package_dir / "package.yaml"
        pkg_yaml.write_text("""
package:
  # Missing name field
  version: "1.0.0"
""")
        
        validator = PackageValidator()
        result, errors = validator.validate_package(test_package_dir)
        
        assert result is False
        assert any("name" in error.lower() for error in errors)
    
    def test_detects_invalid_yaml(self, test_package_dir):
        """Test detection of invalid YAML syntax."""
        pkg_yaml = test_package_dir / "package.yaml"
        pkg_yaml.write_text("invalid: yaml: syntax: [[[")
        
        validator = PackageValidator()
        result, errors = validator.validate_package(test_package_dir)
        
        assert result is False
    
    def test_validates_user_info_fields(self, test_package_dir):
        """Test validation of user_info_fields structure."""
        pkg_yaml = test_package_dir / "package.yaml"
        pkg_yaml.write_text("""
package:
  name: "test"
  version: "1.0.0"
  description: "Test"
  author: "Test"
  
user_info_fields:
  - id: "name"
    label: "Name"
    type: "text"
    required: true
  - id: "email"
    label: "Email"
    type: "email"
    required: false
""")
        
        validator = PackageValidator()
        result, errors = validator.validate_package(test_package_dir)
        
        assert result is True


@pytest.mark.unit
class TestValidateAllPackages:
    """Test bulk package validation."""
    
    def test_validates_multiple_packages(self, temp_dir):
        """Test validation of multiple packages."""
        # Create two valid packages
        for i in range(2):
            pkg_dir = temp_dir / f"package-{i}"
            pkg_dir.mkdir()
            (pkg_dir / "package.yaml").write_text(f"""
package:
  name: "package-{i}"
  version: "1.0.0"
  description: "Test package {i}"
  author: "Test"
""")
        
        valid, invalid = validate_all_packages(temp_dir)
        
        assert len(valid) == 2
        assert len(invalid) == 0
    
    def test_separates_valid_and_invalid(self, temp_dir):
        """Test separation of valid and invalid packages."""
        # Valid package
        valid_dir = temp_dir / "valid"
        valid_dir.mkdir()
        (valid_dir / "package.yaml").write_text("""
package:
  name: "valid"
  version: "1.0.0"
  description: "Valid"
  author: "Test"
""")
        
        # Invalid package
        invalid_dir = temp_dir / "invalid"
        invalid_dir.mkdir()
        (invalid_dir / "package.yaml").write_text("invalid yaml: [[[")
        
        valid, invalid = validate_all_packages(temp_dir)
        
        assert len(valid) == 1
        assert len(invalid) == 1
        assert valid[0]["name"] == "valid"

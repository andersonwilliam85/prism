"""
Integration tests for installer engine.
"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from installer_engine import InstallationEngine


@pytest.mark.integration
class TestInstallerEngine:
    """Test installer engine integration."""
    
    def test_engine_initializes(self, sample_user_info):
        """Test that engine initializes correctly."""
        engine = InstallationEngine(
            config_package="core-prism",
            user_info=sample_user_info
        )
        
        assert engine is not None
        assert engine.user_info == sample_user_info
    
    def test_platform_detection(self):
        """Test platform detection."""
        engine = InstallationEngine(
            config_package="core-prism",
            user_info={"name": "Test", "email": "test@test.com"}
        )
        
        platform = engine._detect_platform()
        
        assert platform in ["macos", "linux", "windows"]
    
    def test_log_callback(self, sample_user_info):
        """Test log callback functionality."""
        logs = []
        
        def callback(step, message, level):
            logs.append({"step": step, "message": message, "level": level})
        
        engine = InstallationEngine(
            config_package="core-prism",
            user_info=sample_user_info,
            progress_callback=callback
        )
        
        engine.log("test", "Test message", "info")
        
        assert len(logs) == 1
        assert logs[0]["step"] == "test"
        assert logs[0]["message"] == "Test message"
        assert logs[0]["level"] == "info"


@pytest.mark.integration
class TestConfigValidation:
    """Test configuration validation integration."""
    
    def test_validates_config_package(self, temp_dir):
        """Test validation of config package."""
        # Create a test package
        pkg_dir = temp_dir / "test-package"
        pkg_dir.mkdir()
        
        (pkg_dir / "package.yaml").write_text("""
package:
  name: "test-package"
  version: "1.0.0"
  description: "Test"
  author: "Test"

user_info_fields:
  - id: "name"
    label: "Name"
    type: "text"
    required: true
""")
        
        # Validation should pass
        from package_validator import PackageValidator
        validator = PackageValidator()
        result, errors = validator.validate_package(pkg_dir)
        
        assert result is True
        assert len(errors) == 0

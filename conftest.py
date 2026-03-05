"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_user_info() -> dict:
    """Sample user information for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "git_username": "testuser"
    }


@pytest.fixture
def test_package_dir(temp_dir: Path) -> Path:
    """Create a test package directory."""
    pkg_dir = temp_dir / "test-package"
    pkg_dir.mkdir(parents=True)
    
    # Create minimal package.yaml
    (pkg_dir / "package.yaml").write_text("""
package:
  name: "test-package"
  version: "1.0.0"
  description: "Test package for unit tests"
  author: "Test Author"
  
user_info_fields:
  - id: "name"
    label: "Name"
    type: "text"
    required: true
""")
    
    return pkg_dir


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override browser launch args to use system Chrome."""
    return {
        **browser_type_launch_args,
        "channel": "chrome",  # Use system Chrome
        "headless": False,
    }


@pytest.fixture(scope="session")
def playwright_browser_args():
    """Browser arguments for Playwright tests."""
    return [
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox",
    ]


@pytest.fixture(scope="session")
def playwright_launch_options(playwright_browser_args):
    """Launch options for Playwright - use system Chrome."""
    return {
        "headless": True,  # Use headless for faster tests
        "args": playwright_browser_args,
        "slow_mo": 0,  # No delay for speed
        "channel": "chrome",  # Use system Chrome instead of downloading browsers
    }

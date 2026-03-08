"""
Pytest configuration and shared fixtures.
"""

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml

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
    }


@pytest.fixture
def prism_dir(temp_dir: Path) -> Path:
    """
    Create a fully valid prism directory with bundled_prisms format.
    Includes a base sub-prism config file on disk.
    """
    pkg_dir = temp_dir / "test-prism"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "base").mkdir()
    (pkg_dir / "teams").mkdir()

    # Write package.yaml
    (pkg_dir / "package.yaml").write_text(
        yaml.dump(
            {
                "package": {
                    "name": "test-prism",
                    "version": "1.0.0",
                    "description": "Test prism for unit tests",
                    "type": "company",
                },
                "prism_config": {
                    "theme": "ocean",
                    "branding": {"name": "Test Prism"},
                },
                "bundled_prisms": {
                    "base": [
                        {
                            "id": "base",
                            "name": "Test Base",
                            "description": "Company-wide defaults",
                            "required": True,
                            "config": "base/test.yaml",
                        }
                    ],
                    "teams": [
                        {
                            "id": "platform",
                            "name": "Platform Team",
                            "config": "teams/platform.yaml",
                        },
                        {
                            "id": "backend",
                            "name": "Backend Team",
                            "config": "teams/backend.yaml",
                        },
                    ],
                },
                "setup": {
                    "install": {
                        "target_dir": "config/",
                        "directories": [{"source": "base/", "dest": "config/base/"}],
                    }
                },
                "user_info_fields": [
                    {"id": "name", "label": "Full Name", "type": "text", "required": True},
                    {"id": "email", "label": "Email", "type": "email", "required": True},
                ],
                "distribution": {"local": {"path": "prisms/test-prism/", "discoverable": True}},
                "metadata": {"tags": ["test"], "company_size": "small"},
            }
        )
    )

    # Write base sub-prism config
    (pkg_dir / "base" / "test.yaml").write_text(
        yaml.dump(
            {
                "company": {"name": "Test Corp", "domain": "test.com"},
                "tools_required": ["git", "docker"],
                "git": {"user": {"email": "${USER}@test.com"}},
                "security": {"sso_required": False},
            }
        )
    )

    # Write team sub-prism configs
    (pkg_dir / "teams" / "platform.yaml").write_text(
        yaml.dump(
            {
                "tools_required": ["kubectl", "terraform"],
                "repositories": [{"name": "infra", "url": "https://github.com/test/infra"}],
            }
        )
    )
    (pkg_dir / "teams" / "backend.yaml").write_text(
        yaml.dump(
            {
                "tools_required": ["python", "postgresql"],
            }
        )
    )

    # Write README
    (pkg_dir / "README.md").write_text("# Test Prism\n")

    return pkg_dir


# Legacy alias for tests that still use the old fixture name
@pytest.fixture
def test_package_dir(prism_dir: Path) -> Path:
    return prism_dir


@pytest.fixture
def mock_progress_callback():
    """A progress callback that records all calls."""
    log = []

    def callback(step, message, level="info"):
        log.append({"step": step, "message": message, "level": level})

    callback.log = log
    return callback

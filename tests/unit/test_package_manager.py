"""
Unit tests for PackageManager.
"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from package_manager import PackageManager


@pytest.mark.unit
class TestDiscoverPackages:
    """Tests for PackageManager.discover_packages()."""

    def test_discovers_prism_with_bundled_prisms(self, temp_dir, prism_dir):
        # prism_dir is already inside temp_dir
        pm = PackageManager(root_dir=prism_dir.parent.parent)
        # Set packages_dir manually to be temp_dir (the parent of prism_dir)
        pm.packages_dir = prism_dir.parent
        packages = pm.discover_packages()
        names = [p["name"] for p in packages]
        assert "test-prism" in names

    def test_discovers_multiple_prisms(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        for i in range(3):
            pkg_dir = prisms_dir / f"prism-{i}"
            pkg_dir.mkdir()
            (pkg_dir / "package.yaml").write_text(
                yaml.dump(
                    {
                        "package": {"name": f"prism-{i}", "version": "1.0.0", "description": f"Prism {i}"},
                    }
                )
            )

        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert len(packages) == 3

    def test_skips_directory_without_package_yaml(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        (prisms_dir / "no-yaml").mkdir()
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert len(packages) == 0

    def test_skips_non_discoverable_prism(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "hidden-prism"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "hidden-prism", "version": "1.0.0", "description": "Hidden"},
                    "distribution": {"local": {"path": "prisms/hidden-prism/", "discoverable": False}},
                }
            )
        )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert len(packages) == 0

    def test_result_includes_tiers_for_bundled_prisms(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "tiered"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "tiered", "version": "1.0.0", "description": "Tiered"},
                    "bundled_prisms": {
                        "base": [{"id": "base", "name": "Base", "required": True, "config": "base/base.yaml"}],
                        "roles": [{"id": "dev", "name": "Developer", "config": "roles/dev.yaml"}],
                    },
                }
            )
        )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert len(packages) == 1
        tiers = packages[0]["tiers"]
        assert "base" in tiers
        assert "roles" in tiers
        assert tiers["base"][0]["id"] == "base"
        assert tiers["base"][0]["required"] is True

    def test_result_includes_has_bundled_prisms_flag(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "bundled"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "bundled", "version": "1.0.0", "description": "Bundled"},
                    "bundled_prisms": {"base": [{"id": "b", "name": "B", "config": "b/b.yaml"}]},
                }
            )
        )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert packages[0]["has_bundled_prisms"] is True

    def test_result_without_bundled_prisms(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "simple"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "simple", "version": "1.0.0", "description": "Simple"},
                }
            )
        )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert packages[0]["has_bundled_prisms"] is False

    def test_empty_prisms_directory(self, temp_dir):
        (temp_dir / "prisms").mkdir()
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert packages == []

    def test_nonexistent_prisms_directory(self, temp_dir):
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert packages == []

    def test_result_sorted_by_name(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        for name in ["zebra", "alpha", "middle"]:
            pkg_dir = prisms_dir / name
            pkg_dir.mkdir()
            (pkg_dir / "package.yaml").write_text(
                yaml.dump(
                    {
                        "package": {"name": name, "version": "1.0.0", "description": name},
                    }
                )
            )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        names = [p["name"] for p in packages]
        assert names == sorted(names)

    def test_theme_extracted_from_prism_config(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pkg_dir = prisms_dir / "themed"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "themed", "version": "1.0.0", "description": "Themed"},
                    "prism_config": {"theme": "midnight"},
                }
            )
        )
        pm = PackageManager(root_dir=temp_dir)
        packages = pm.discover_packages()
        assert packages[0]["theme"] == "midnight"


@pytest.mark.unit
class TestCreatePackageScaffold:
    """Tests for PackageManager.create_package_scaffold()."""

    def test_creates_directory_structure(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        result = pm.create_package_scaffold("mycompany", "My Company Inc")
        assert result is True
        pkg_dir = prisms_dir / "mycompany"
        assert pkg_dir.exists()
        assert (pkg_dir / "base").exists()
        assert (pkg_dir / "teams").exists()

    def test_creates_package_yaml_with_new_format(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("testcorp", "Test Corp")
        pkg_yaml = prisms_dir / "testcorp" / "package.yaml"
        assert pkg_yaml.exists()
        data = yaml.safe_load(pkg_yaml.read_text())
        assert "bundled_prisms" in data
        assert "prism_config" in data
        assert "setup" in data
        assert "user_info_fields" in data

    def test_creates_base_config_file(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("testcorp", "Test Corp")
        base_file = prisms_dir / "testcorp" / "base" / "testcorp.yaml"
        assert base_file.exists()

    def test_creates_team_config_files(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("testcorp", "Test Corp")
        assert (prisms_dir / "testcorp" / "teams" / "platform.yaml").exists()
        assert (prisms_dir / "testcorp" / "teams" / "backend.yaml").exists()

    def test_creates_readme(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("testcorp", "Test Corp")
        readme = prisms_dir / "testcorp" / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "Test Corp" in content

    def test_returns_false_if_already_exists(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        (prisms_dir / "existing").mkdir()
        pm = PackageManager(root_dir=temp_dir)
        result = pm.create_package_scaffold("existing", "Existing")
        assert result is False

    def test_company_name_derived_from_package_name(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("my-startup")  # No explicit company name
        pkg_yaml = prisms_dir / "my-startup" / "package.yaml"
        assert pkg_yaml.exists()

    def test_generated_package_yaml_has_required_fields(self, temp_dir):
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("newcorp", "New Corp")
        data = yaml.safe_load((prisms_dir / "newcorp" / "package.yaml").read_text())
        assert data["package"]["version"] == "1.0.0"
        assert "name" in data["package"]
        assert "description" in data["package"]

    def test_bundled_prisms_references_exist_on_disk(self, temp_dir):
        """Scaffold's bundled_prisms config references must exist after creation."""
        prisms_dir = temp_dir / "prisms"
        prisms_dir.mkdir()
        pm = PackageManager(root_dir=temp_dir)
        pm.create_package_scaffold("newcorp", "New Corp")
        data = yaml.safe_load((prisms_dir / "newcorp" / "package.yaml").read_text())
        for tier_name, tier_items in data.get("bundled_prisms", {}).items():
            for item in tier_items:
                config_path = prisms_dir / "newcorp" / item["config"]
                assert config_path.exists(), f"Missing config file: {item['config']}"

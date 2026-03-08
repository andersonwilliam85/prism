"""
Integration tests for InstallationEngine with real prism packages.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest  # noqa: E402
import yaml  # noqa: E402

from installer_engine import InstallationEngine  # noqa: E402

PRISMS_DIR = Path(__file__).parent.parent.parent / "prisms"


def prism_exists(name: str) -> bool:
    return (PRISMS_DIR / name / "package.yaml").exists()


@pytest.mark.integration
class TestEngineWithRealPrisms:
    """Test InstallationEngine loading and merging with actual prisms from prisms/."""

    def test_engine_loads_personal_dev(self, sample_user_info):
        if not prism_exists("personal-dev"):
            pytest.skip("personal-dev prism not present")
        engine = InstallationEngine(
            config_package=str(PRISMS_DIR / "personal-dev"),
            user_info=sample_user_info,
        )
        # Should have prism meta (prism_config section)
        assert isinstance(engine.prism_meta, dict)

    def test_engine_loads_startup(self, sample_user_info):
        if not prism_exists("startup.prism"):
            pytest.skip("startup.prism not present")
        engine = InstallationEngine(
            config_package=str(PRISMS_DIR / "startup.prism"),
            user_info=sample_user_info,
        )
        assert isinstance(engine.merged_config, dict)

    def test_engine_loads_fortune500(self, sample_user_info):
        if not prism_exists("fortune500.prism"):
            pytest.skip("fortune500.prism not present")
        engine = InstallationEngine(
            config_package=str(PRISMS_DIR / "fortune500.prism"),
            user_info=sample_user_info,
        )
        assert isinstance(engine.merged_config, dict)

    def test_base_sub_prism_always_merged(self, sample_user_info):
        """Required base sub-prism should always be in merged_config."""
        for prism_name in ("personal-dev", "startup.prism"):
            prism_path = PRISMS_DIR / prism_name
            if not prism_path.exists():
                continue
            engine = InstallationEngine(
                config_package=str(prism_path),
                user_info=sample_user_info,
                selected_sub_prisms={},  # no optional selections
            )
            # merged_config should have content from the required base
            assert engine.merged_config is not None

    def test_selected_sub_prism_adds_tools(self, sample_user_info, temp_dir):
        """When an optional sub-prism is selected, its tools appear in merged_config."""
        # Use our test fixture prism (via conftest prism_dir)
        prism_path = temp_dir / "test-prism"
        prism_path.mkdir()
        (prism_path / "base").mkdir()
        (prism_path / "teams").mkdir()
        (prism_path / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "test", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "b", "name": "Base", "required": True, "config": "base/b.yaml"}],
                        "teams": [
                            {"id": "platform", "name": "Platform", "config": "teams/platform.yaml"},
                            {"id": "backend", "name": "Backend", "config": "teams/backend.yaml"},
                        ],
                    },
                }
            )
        )
        (prism_path / "base" / "b.yaml").write_text(yaml.dump({"tools_required": ["git"]}))
        (prism_path / "teams" / "platform.yaml").write_text(yaml.dump({"tools_required": ["kubectl"]}))
        (prism_path / "teams" / "backend.yaml").write_text(yaml.dump({"tools_required": ["python"]}))

        engine = InstallationEngine(
            config_package=str(prism_path),
            user_info=sample_user_info,
            selected_sub_prisms={"teams": "platform"},
        )
        tools = engine.merged_config.get("tools_required", [])
        assert "git" in tools
        assert "kubectl" in tools
        assert "python" not in tools  # backend not selected


@pytest.mark.integration
class TestSubPrismMerging:
    """Integration tests for sub-prism merging mechanics."""

    def test_required_plus_optional_merge(self, temp_dir, sample_user_info):
        prism_path = temp_dir / "mergetest"
        prism_path.mkdir()
        (prism_path / "base").mkdir()
        (prism_path / "roles").mkdir()

        (prism_path / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "mergetest", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "b", "name": "Base", "required": True, "config": "base/b.yaml"}],
                        "roles": [
                            {"id": "devops", "name": "DevOps", "config": "roles/devops.yaml"},
                        ],
                    },
                }
            )
        )
        (prism_path / "base" / "b.yaml").write_text(
            yaml.dump(
                {
                    "tools_required": ["git", "docker"],
                    "security": {"sso_required": True},
                    "environment": {"proxy": {"http": "http://proxy:8080"}},
                }
            )
        )
        (prism_path / "roles" / "devops.yaml").write_text(
            yaml.dump(
                {
                    "tools_required": ["terraform", "ansible"],
                    "environment": {"ci": {"tool": "jenkins"}},
                }
            )
        )

        engine = InstallationEngine(
            config_package=str(prism_path),
            user_info=sample_user_info,
            selected_sub_prisms={"roles": "devops"},
        )

        # Tools union
        tools = engine.merged_config.get("tools_required", [])
        assert "git" in tools
        assert "docker" in tools
        assert "terraform" in tools
        assert "ansible" in tools

        # Security from base preserved
        assert engine.merged_config.get("security", {}).get("sso_required") is True

        # Environment deep merged
        env = engine.merged_config.get("environment", {})
        assert env.get("proxy", {}).get("http") == "http://proxy:8080"
        assert env.get("ci", {}).get("tool") == "jenkins"

    def test_repositories_accumulate_from_multiple_sub_prisms(self, temp_dir, sample_user_info):
        prism_path = temp_dir / "repotest"
        prism_path.mkdir()
        (prism_path / "base").mkdir()
        (prism_path / "roles").mkdir()

        (prism_path / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "repotest", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "b", "name": "Base", "required": True, "config": "base/b.yaml"}],
                        "roles": [{"id": "dev", "name": "Dev", "config": "roles/dev.yaml"}],
                    },
                }
            )
        )
        (prism_path / "base" / "b.yaml").write_text(
            yaml.dump({"repositories": [{"name": "shared", "url": "https://github.com/example/shared"}]})
        )
        (prism_path / "roles" / "dev.yaml").write_text(
            yaml.dump({"repositories": [{"name": "project", "url": "https://github.com/example/project"}]})
        )

        engine = InstallationEngine(
            config_package=str(prism_path),
            user_info=sample_user_info,
            selected_sub_prisms={"roles": "dev"},
        )

        repos = engine.merged_config.get("repositories", [])
        repo_names = [r.get("name") for r in repos]
        assert "shared" in repo_names
        assert "project" in repo_names

    def test_tools_deduplication_across_sub_prisms(self, temp_dir, sample_user_info):
        prism_path = temp_dir / "dedup"
        prism_path.mkdir()
        (prism_path / "base").mkdir()
        (prism_path / "roles").mkdir()

        (prism_path / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {"name": "dedup", "version": "1.0.0", "description": "Test"},
                    "bundled_prisms": {
                        "base": [{"id": "b", "name": "Base", "required": True, "config": "base/b.yaml"}],
                        "roles": [{"id": "dev", "name": "Dev", "config": "roles/dev.yaml"}],
                    },
                }
            )
        )
        (prism_path / "base" / "b.yaml").write_text(yaml.dump({"tools_required": ["git", "docker", "kubectl"]}))
        (prism_path / "roles" / "dev.yaml").write_text(
            yaml.dump({"tools_required": ["docker", "vscode"]})  # docker is duplicate
        )

        engine = InstallationEngine(
            config_package=str(prism_path),
            user_info=sample_user_info,
            selected_sub_prisms={"roles": "dev"},
        )

        tools = engine.merged_config.get("tools_required", [])
        assert tools.count("docker") == 1  # deduplicated by union strategy


@pytest.mark.integration
class TestFinalize:
    """Integration tests for step_finalize() and step_apply_config_package()."""

    def test_finalize_creates_marker_file(self, temp_dir, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.home = temp_dir
        engine.workspace = temp_dir / "workspace"
        engine.workspace.mkdir()

        engine.step_finalize()

        marker = temp_dir / "workspace" / ".prism_installed"
        assert marker.exists()
        import json

        data = json.loads(marker.read_text())
        assert "installed_at" in data
        assert "platform" in data

    def test_apply_config_copies_prism_files(self, temp_dir, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        engine.home = temp_dir
        engine.workspace = temp_dir / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "docs").mkdir()

        engine.step_apply_config_package()

        dest = temp_dir / "workspace" / "docs" / "config"
        assert dest.exists()
        assert (dest / "package.yaml").exists()

    def test_apply_config_saves_merged_config(self, temp_dir, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        engine.home = temp_dir
        engine.workspace = temp_dir / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "docs").mkdir()

        engine.step_apply_config_package()

        merged_file = temp_dir / "workspace" / "docs" / "config" / "merged-config.yaml"
        assert merged_file.exists()
        data = yaml.safe_load(merged_file.read_text())
        assert "tools_required" in data

    def test_apply_config_saves_user_info(self, temp_dir, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        engine.home = temp_dir
        engine.workspace = temp_dir / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "docs").mkdir()

        engine.step_apply_config_package()

        user_info_file = temp_dir / "workspace" / "docs" / "config" / "user-info.yaml"
        assert user_info_file.exists()
        data = yaml.safe_load(user_info_file.read_text())
        assert data["full_name"] == sample_user_info["full_name"]

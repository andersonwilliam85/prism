"""
Unit tests for InstallationEngine.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from installer_engine import InstallationEngine


@pytest.mark.unit
class TestEngineInitialization:
    """Tests for engine setup and initialization."""

    def test_init_without_config(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        assert engine is not None
        assert engine.user_info == sample_user_info
        assert engine.merged_config == {}
        assert engine.prism_meta == {}

    def test_init_with_config_package(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        assert engine.config_package == str(prism_dir)

    def test_init_populates_prism_meta(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        assert engine.prism_meta.get("theme") == "ocean"
        assert engine.prism_meta.get("branding", {}).get("name") == "Test Prism"

    def test_init_merges_required_base_sub_prism(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        # base/test.yaml has tools_required: [git, docker]
        tools = engine.merged_config.get("tools_required", [])
        assert "git" in tools
        assert "docker" in tools

    def test_init_selects_optional_sub_prism(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
            selected_sub_prisms={"teams": "platform"},
        )
        # platform.yaml adds kubectl, terraform
        tools = engine.merged_config.get("tools_required", [])
        assert "kubectl" in tools
        assert "terraform" in tools

    def test_init_non_selected_tier_not_merged(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
            selected_sub_prisms={"teams": "platform"},
        )
        # backend.yaml adds python, postgresql — should NOT be merged
        tools = engine.merged_config.get("tools_required", [])
        assert "python" not in tools
        assert "postgresql" not in tools

    def test_init_no_selection_for_optional_tier(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
            selected_sub_prisms={},  # no teams selection
        )
        # Only base sub-prism merged (git, docker)
        tools = engine.merged_config.get("tools_required", [])
        assert "git" in tools
        assert "kubectl" not in tools
        assert "python" not in tools

    def test_init_nonexistent_package_path(self, temp_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(temp_dir / "nonexistent"),
            user_info=sample_user_info,
        )
        assert engine.merged_config == {}
        assert engine.prism_meta == {}

    def test_selected_sub_prisms_stored(self, sample_user_info):
        selections = {"teams": "platform", "roles": "devops"}
        engine = InstallationEngine(
            user_info=sample_user_info,
            selected_sub_prisms=selections,
        )
        assert engine.selected_sub_prisms == selections

    def test_user_info_defaults_to_empty_dict(self):
        engine = InstallationEngine()
        assert engine.user_info == {}

    def test_selected_sub_prisms_defaults_to_empty_dict(self):
        engine = InstallationEngine()
        assert engine.selected_sub_prisms == {}


@pytest.mark.unit
class TestPlatformDetection:
    """Tests for _detect_platform()."""

    def test_returns_platform_tuple(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        platform_name, platform_detail = engine.platform_name, engine.platform_detail
        assert platform_name in {"mac", "linux", "ubuntu", "windows", "unknown"}
        assert isinstance(platform_detail, str)

    def test_detect_platform_on_linux(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        with patch("platform.system", return_value="Linux"):
            with patch("builtins.open", side_effect=FileNotFoundError):
                name, detail = engine._detect_platform()
        assert name == "linux"

    def test_detect_platform_on_macos(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.machine", return_value="x86_64"):
                name, detail = engine._detect_platform()
        assert name == "mac"
        assert detail == "Intel"

    def test_detect_platform_apple_silicon(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.machine", return_value="arm64"):
                name, detail = engine._detect_platform()
        assert name == "mac"
        assert detail == "Apple Silicon"

    def test_detect_platform_windows(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        with patch("platform.system", return_value="Windows"):
            with patch("platform.version", return_value="10.0"):
                name, detail = engine._detect_platform()
        assert name == "windows"


@pytest.mark.unit
class TestLogging:
    """Tests for the log() method and progress callback."""

    def test_log_calls_callback(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.log("test_step", "Test message", "info")
        assert len(mock_progress_callback.log) == 1
        entry = mock_progress_callback.log[0]
        assert entry["step"] == "test_step"
        assert entry["message"] == "Test message"
        assert entry["level"] == "info"

    def test_log_all_levels(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        for level in ("info", "success", "error", "warning"):
            engine.log("step", f"Message at {level}", level)

        levels = [e["level"] for e in mock_progress_callback.log]
        assert "info" in levels
        assert "success" in levels
        assert "error" in levels
        assert "warning" in levels

    def test_log_without_callback_does_not_raise(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.log("step", "message")  # Should not raise

    def test_log_appends_all_calls(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        for i in range(5):
            engine.log("step", f"Message {i}")
        assert len(mock_progress_callback.log) == 5


@pytest.mark.unit
class TestGetToolsFromMergedConfig:
    """Tests for _get_tools_from_merged_config()."""

    def test_reads_tools_from_merged_config(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
        )
        tools = engine._get_tools_from_merged_config()
        assert isinstance(tools, list)
        assert "git" in tools

    def test_returns_empty_when_no_config(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.merged_config = {}
        tools = engine._get_tools_from_merged_config()
        assert tools == []

    def test_tools_with_selected_sub_prism(self, prism_dir, sample_user_info):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
            selected_sub_prisms={"teams": "platform"},
        )
        tools = engine._get_tools_from_merged_config()
        assert "kubectl" in tools
        assert "terraform" in tools

    def test_legacy_package_tools_fallback(self, temp_dir, sample_user_info):
        """When merged_config is empty, falls back to package.tools."""
        pkg_dir = temp_dir / "legacy-prism"
        pkg_dir.mkdir()
        (pkg_dir / "package.yaml").write_text(
            yaml.dump(
                {
                    "package": {
                        "name": "legacy",
                        "version": "1.0.0",
                        "description": "Legacy",
                        "tools": ["git", "vim"],
                    }
                }
            )
        )
        engine = InstallationEngine(
            config_package=str(pkg_dir),
            user_info=sample_user_info,
        )
        tools = engine._get_tools_from_merged_config()
        assert "git" in tools or "vim" in tools  # legacy format


@pytest.mark.unit
class TestGitConfig:
    """Tests for step_configure_git()."""

    def test_configures_git_from_user_info(self, tmp_path, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        with patch.object(engine, "run_command") as mock_run:
            engine.step_configure_git()
            calls = [str(c) for c in mock_run.call_args_list]
            assert any("Jane Doe" in c for c in calls)
            assert any("jane@example.com" in c for c in calls)

    def test_skips_git_config_when_no_user_info(self, mock_progress_callback):
        engine = InstallationEngine(
            user_info={},
            progress_callback=mock_progress_callback,
        )
        with patch.object(engine, "run_command") as mock_run:
            engine.step_configure_git()
            # Should skip, not call git config
            mock_run.assert_not_called()

    def test_uses_merged_config_git_as_fallback(self, prism_dir, mock_progress_callback):
        """If user_info lacks name/email, fall back to git section in merged_config."""
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info={},
            progress_callback=mock_progress_callback,
        )
        # prism_dir's base yaml has: git.user.email: "${USER}@test.com"
        # After env var substitution, this should be used
        with patch.object(engine, "run_command"):
            # Should not raise — it either uses merged_config.git or skips
            engine.step_configure_git()

    def test_git_config_uses_full_name_key(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info={"full_name": "Full Name User", "email": "fn@example.com"},
            progress_callback=mock_progress_callback,
        )
        with patch.object(engine, "run_command") as mock_run:
            engine.step_configure_git()
            calls = [str(c) for c in mock_run.call_args_list]
            assert any("Full Name User" in c for c in calls)


@pytest.mark.unit
class TestStepFolderStructure:
    """Tests for step_create_folder_structure()."""

    def test_creates_workspace_folders(self, sample_user_info, tmp_path):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        engine.step_create_folder_structure()
        assert (tmp_path / "workspace").exists()
        assert (tmp_path / "workspace" / "projects").exists()
        assert (tmp_path / "workspace" / "experiments").exists()
        assert (tmp_path / "workspace" / "docs").exists()

    def test_does_not_fail_if_folders_exist(self, sample_user_info, tmp_path):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        engine.step_create_folder_structure()
        # Running again should not raise
        engine.step_create_folder_structure()


@pytest.mark.unit
class TestStepCloneRepositories:
    """Tests for step_clone_repositories()."""

    def test_skips_when_no_repositories(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.merged_config = {}
        with patch.object(engine, "run_command") as mock_run:
            engine.step_clone_repositories()
            mock_run.assert_not_called()

    def test_skips_existing_repo_directory(self, sample_user_info, tmp_path, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        (tmp_path / "workspace" / "projects").mkdir(parents=True)
        existing_dir = tmp_path / "workspace" / "projects" / "myrepo"
        existing_dir.mkdir()

        engine.merged_config = {"repositories": [{"name": "myrepo", "url": "https://github.com/example/myrepo"}]}
        with patch.object(engine, "run_command") as mock_run:
            engine.step_clone_repositories()
            mock_run.assert_not_called()

    def test_clones_repo_string_format(self, sample_user_info, tmp_path, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "projects").mkdir()

        engine.merged_config = {"repositories": ["https://github.com/example/myrepo.git"]}
        with patch.object(engine, "run_command") as mock_run:
            engine.step_clone_repositories()
            assert mock_run.called

    def test_clones_repo_dict_format(self, sample_user_info, tmp_path, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "projects").mkdir()

        engine.merged_config = {"repositories": [{"name": "infra", "url": "https://github.com/example/infra"}]}
        with patch.object(engine, "run_command") as mock_run:
            engine.step_clone_repositories()
            assert mock_run.called

    def test_clone_failure_does_not_raise(self, sample_user_info, tmp_path, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.home = tmp_path
        engine.workspace = tmp_path / "workspace"
        engine.workspace.mkdir(parents=True)
        (engine.workspace / "projects").mkdir()

        engine.merged_config = {"repositories": [{"name": "broken", "url": "https://invalid.example.com/broken"}]}
        with patch.object(engine, "run_command", side_effect=Exception("clone failed")):
            # Should not raise — failure is logged as warning
            engine.step_clone_repositories()


@pytest.mark.unit
class TestStepApplyPrismConfig:
    """Tests for step_apply_prism_config()."""

    def test_no_prism_meta_logs_info(self, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        engine.prism_meta = {}
        engine.step_apply_prism_config()
        messages = [e["message"] for e in mock_progress_callback.log]
        assert any("defaults" in m for m in messages)

    def test_theme_logged(self, prism_dir, sample_user_info, mock_progress_callback):
        engine = InstallationEngine(
            config_package=str(prism_dir),
            user_info=sample_user_info,
            progress_callback=mock_progress_callback,
        )
        mock_progress_callback.log.clear()
        engine.step_apply_prism_config()
        messages = [e["message"] for e in mock_progress_callback.log]
        assert any("ocean" in m.lower() for m in messages)

    def test_proxy_applied_to_env(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.prism_meta = {
            "proxies": {
                "http": "http://proxy.example.com:8080",
                "https": "http://proxy.example.com:8080",
            }
        }
        engine._apply_proxy_settings()
        assert os.environ.get("HTTP_PROXY") == "http://proxy.example.com:8080"
        # Clean up
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("https_proxy", None)

    def test_no_proxy_does_not_set_env(self, sample_user_info):
        engine = InstallationEngine(user_info=sample_user_info)
        engine.prism_meta = {}
        engine.merged_config = {}
        os.environ.pop("HTTP_PROXY", None)
        engine._apply_proxy_settings()
        assert "HTTP_PROXY" not in os.environ

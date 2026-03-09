"""Unit tests for InstallationManager.

BDT: Manager tier — real engines, mocked accessors.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prism.engines.merge_engine.merge_engine import MergeEngine
from prism.engines.setup_engine.setup_engine import SetupEngine
from prism.engines.validation_engine.validation_engine import ValidationEngine
from prism.managers.installation_manager.installation_manager import InstallationManager
from prism.utilities.event_bus.in_memory_event_bus import InMemoryEventBus

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def file_accessor():
    mock = MagicMock()
    mock.exists.return_value = False
    mock.find_package.return_value = Path("/fake/prisms/startup")
    mock.read_yaml.return_value = {}
    return mock


@pytest.fixture
def command_accessor():
    mock = MagicMock()
    mock.pkg_is_installed.return_value = True
    mock.ssh_key_exists.return_value = True
    return mock


@pytest.fixture
def system_accessor():
    mock = MagicMock()
    mock.get_platform.return_value = ("mac", "Apple Silicon")
    mock.get_installed_version.return_value = "3.11"
    return mock


@pytest.fixture
def event_bus():
    return InMemoryEventBus()


@pytest.fixture
def prisms_dir():
    return Path("/fake/prisms")


@pytest.fixture
def valid_config():
    return {
        "package": {
            "name": "startup",
            "version": "1.0.0",
            "description": "Startup Prism",
        },
        "prism_config": {"theme": "ocean"},
        "bundled_prisms": {},
    }


@pytest.fixture
def manager(file_accessor, command_accessor, system_accessor, event_bus, prisms_dir):
    return InstallationManager(
        merge_engine=MergeEngine(),
        setup_engine=SetupEngine(),
        validation_engine=ValidationEngine(),
        command_accessor=command_accessor,
        file_accessor=file_accessor,
        system_accessor=system_accessor,
        event_bus=event_bus,
        prisms_dir=prisms_dir,
    )


# ------------------------------------------------------------------
# install — happy path
# ------------------------------------------------------------------


class TestInstallHappyPath:
    def test_successful_install(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {"name": "Alice", "email": "alice@test.com"})
        assert result.success is True
        assert result.package_name == "startup"
        assert result.error is None
        assert len(result.steps) > 0

    def test_publishes_complete_event(self, manager, file_accessor, event_bus, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        events = []
        event_bus.subscribe("installation.complete", lambda payload: events.append(payload))
        manager.install("startup", {"name": "Bob"})
        assert len(events) == 1
        assert events[0]["package"] == "startup"
        assert events[0]["success"] is True

    def test_creates_workspace_dirs(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {})
        # Should have called mkdir for workspace subdirectories
        mkdir_calls = file_accessor.mkdir.call_args_list
        assert len(mkdir_calls) >= 6  # projects, experiments, learning, archived, docs, tooling

    def test_configures_git(self, manager, file_accessor, command_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {"name": "Alice", "email": "alice@test.com"})
        # git_set_config should be called for user.name, user.email, init.defaultBranch, pull.rebase
        assert command_accessor.git_set_config.call_count >= 4


# ------------------------------------------------------------------
# install — failure paths
# ------------------------------------------------------------------


class TestInstallFailures:
    def test_validation_failure(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {"package": {}}
        result = manager.install("bad-prism", {})
        assert result.success is False
        assert "Validation failed" in result.error

    def test_unsupported_platform(self, manager, file_accessor, system_accessor, valid_config):
        system_accessor.get_platform.return_value = ("unknown", "")
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {})
        assert result.success is False
        assert "Unsupported platform" in result.error

    def test_preflight_failure(self, manager, file_accessor, system_accessor):
        config = {
            "package": {
                "name": "strict",
                "version": "1.0.0",
                "description": "Strict",
                "requires": {"node": True},
            },
        }
        system_accessor.get_installed_version.return_value = None
        file_accessor.get_package_config.return_value = config
        result = manager.install("strict", {})
        assert result.success is False
        assert "Preflight failed" in result.error

    def test_publishes_failed_event(self, manager, file_accessor, event_bus):
        file_accessor.get_package_config.side_effect = FileNotFoundError("not found")
        events = []
        event_bus.subscribe("installation.failed", lambda payload: events.append(payload))
        result = manager.install("missing", {})
        assert result.success is False
        assert len(events) == 1


# ------------------------------------------------------------------
# install — tool filtering
# ------------------------------------------------------------------


class TestToolFiltering:
    def test_tools_excluded(self, manager, file_accessor, command_accessor, valid_config):
        valid_config["bundled_prisms"] = {}
        file_accessor.get_package_config.return_value = valid_config
        # No tools_required in config, so nothing to filter — just ensure it doesn't crash
        result = manager.install("startup", {}, tools_excluded=["docker"])
        assert result.success is True


# ------------------------------------------------------------------
# check_readiness
# ------------------------------------------------------------------


class TestCheckReadiness:
    def test_all_satisfied(self, manager, system_accessor):
        system_accessor.get_installed_version.return_value = "3.11"
        ok, failures = manager.check_readiness({"python_version": ">=3.8"})
        assert ok is True
        assert failures == []

    def test_missing_tool(self, manager, system_accessor):
        system_accessor.get_installed_version.return_value = None
        ok, failures = manager.check_readiness({"docker": True})
        assert ok is False
        assert any("docker" in f for f in failures)


# ------------------------------------------------------------------
# load_prism_config
# ------------------------------------------------------------------


class TestLoadPrismConfig:
    def test_loads_config(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {
            "prism_config": {
                "theme": "purple",
                "npm_registry": "https://registry.example.com",
                "branding": {"logo_text": "Acme"},
            }
        }
        config = manager.load_prism_config("acme")
        assert config.theme == "purple"
        assert config.npm_registry == "https://registry.example.com"
        assert config.branding.logo_text == "Acme"

    def test_defaults_when_empty(self, manager, file_accessor):
        file_accessor.get_package_config.return_value = {}
        config = manager.load_prism_config("minimal")
        assert config.theme == "ocean"


# ------------------------------------------------------------------
# merge_tiers
# ------------------------------------------------------------------


class TestMergeTiers:
    def test_merges_required_tiers(self, manager, file_accessor):
        config = {
            "package": {"name": "test"},
            "bundled_prisms": {
                "base": [{"id": "core", "config": "configs/core.yaml", "required": True}],
            },
        }
        file_accessor.find_package.return_value = Path("/fake/prisms/test")
        file_accessor.exists.return_value = True
        file_accessor.read_yaml.return_value = {"tools_required": ["git", "node"]}

        merged = manager.merge_tiers(config, {})
        assert "tools_required" in merged
        assert "git" in merged["tools_required"]

    def test_empty_when_no_bundled(self, manager, file_accessor):
        config = {"package": {"name": "test"}}
        assert manager.merge_tiers(config, {}) == {}


# ------------------------------------------------------------------
# progress callback
# ------------------------------------------------------------------


class TestProgressCallback:
    def test_callback_receives_log_messages(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        messages = []
        manager.set_progress_callback(lambda step, msg, level: messages.append((step, msg, level)))
        manager.install("startup", {})
        assert len(messages) > 0
        steps = [m[0] for m in messages]
        assert "platform" in steps


# ------------------------------------------------------------------
# Configurable workspace (BL-010)
# ------------------------------------------------------------------


class TestConfigurableWorkspace:
    def test_custom_workspace_dir(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {"workspace_dir": "/tmp/myworkspace"})
        # Should create dirs under /tmp/myworkspace, not ~/workspace
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        assert any("/tmp/myworkspace" in p for p in paths)

    def test_default_workspace_when_not_specified(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {})
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        assert any("workspace" in p for p in paths)

    def test_tilde_expansion(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {"workspace_dir": "~/development"})
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        # ~ should be expanded, not literal
        assert not any("~" in p for p in paths)

    def test_config_driven_directories(self, manager, file_accessor):
        config = {
            "package": {"name": "custom", "version": "1.0.0", "description": "Custom"},
            "setup": {
                "install": {
                    "directories": [
                        {"name": "src"},
                        {"name": "infra"},
                        {"name": "sandbox"},
                    ]
                }
            },
        }
        file_accessor.get_package_config.return_value = config
        manager.install("custom", {})
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        assert any("src" in p for p in paths)
        assert any("infra" in p for p in paths)
        assert any("sandbox" in p for p in paths)


# ------------------------------------------------------------------
# Two-phase install (privilege separation)
# ------------------------------------------------------------------


class TestTwoPhaseInstall:
    def test_skip_privileged_returns_phase_1(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {}, skip_privileged=True)
        assert result.success is True
        assert result.phase == 1

    def test_skip_privileged_defers_tools(self, manager, file_accessor, command_accessor):
        config = {
            "package": {"name": "test", "version": "1.0.0", "description": "Test"},
            "tools_required": [{"name": "docker", "description": "Containers"}],
        }
        file_accessor.get_package_config.return_value = config
        command_accessor.pkg_is_installed.return_value = False

        result = manager.install("test", {}, skip_privileged=True)
        assert result.success is True
        assert result.phase == 1
        assert len(result.pending_privileged) == 1
        assert result.pending_privileged[0].name == "docker"

    def test_skip_privileged_tools_step_marked_skipped(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {}, skip_privileged=True)
        tools_steps = [s for s in result.steps if s.step == "tools"]
        assert any(s.skipped for s in tools_steps)

    def test_normal_install_is_phase_2(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {})
        assert result.phase == 2

    def test_normal_install_no_pending(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {})
        assert result.pending_privileged == []


class TestPlanPrivilegedInstalls:
    def test_no_tools_returns_empty(self, manager):
        plan = manager.plan_privileged_installs({}, "mac")
        assert plan == []

    def test_already_installed_tools_excluded(self, manager, command_accessor):
        command_accessor.pkg_is_installed.return_value = True
        config = {"tools_required": [{"name": "git"}]}
        plan = manager.plan_privileged_installs(config, "mac")
        assert plan == []

    def test_missing_tools_included(self, manager, command_accessor):
        command_accessor.pkg_is_installed.return_value = False
        config = {"tools_required": [{"name": "docker"}, {"name": "kubectl"}]}
        plan = manager.plan_privileged_installs(config, "ubuntu")
        assert len(plan) == 2
        assert plan[0].name == "docker"
        assert plan[1].name == "kubectl"

    def test_mac_no_sudo(self, manager, command_accessor):
        command_accessor.pkg_is_installed.return_value = False
        config = {"tools_required": [{"name": "node"}]}
        plan = manager.plan_privileged_installs(config, "mac")
        assert len(plan) == 1
        assert plan[0].needs_sudo is False
        assert "brew" in plan[0].command

    def test_ubuntu_needs_sudo(self, manager, command_accessor):
        command_accessor.pkg_is_installed.return_value = False
        config = {"tools_required": [{"name": "node"}]}
        plan = manager.plan_privileged_installs(config, "ubuntu")
        assert len(plan) == 1
        assert plan[0].needs_sudo is True
        assert "apt" in plan[0].command

    def test_windows_needs_sudo(self, manager, command_accessor):
        command_accessor.pkg_is_installed.return_value = False
        config = {"tools_required": [{"name": "git"}]}
        plan = manager.plan_privileged_installs(config, "windows")
        assert len(plan) == 1
        assert plan[0].needs_sudo is True
        assert "choco" in plan[0].command


class TestInstallPrivileged:
    def test_installs_pending_tools(self, manager, command_accessor):
        from prism.models.installation import PrivilegedStep

        steps = [
            PrivilegedStep(
                name="docker",
                command="brew install docker",
                needs_sudo=False,
                platform="mac",
            ),
        ]
        command_accessor.pkg_is_installed.return_value = False
        result = manager.install_privileged(steps, "mac")
        assert result.success is True
        assert result.phase == 2
        command_accessor.pkg_install.assert_called_once_with("docker", "mac")

    def test_skips_already_installed(self, manager, command_accessor):
        from prism.models.installation import PrivilegedStep

        steps = [
            PrivilegedStep(name="git", command="brew install git", needs_sudo=False, platform="mac"),
        ]
        command_accessor.pkg_is_installed.return_value = True
        result = manager.install_privileged(steps, "mac")
        assert result.success is True
        command_accessor.pkg_install.assert_not_called()

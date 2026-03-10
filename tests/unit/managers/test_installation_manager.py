"""Unit tests for InstallationManager.

BDT: Manager tier — real engines, mocked accessors.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prism.engines.config_engine.config_engine import ConfigEngine
from prism.engines.installation_engine.installation_engine import InstallationEngine
from prism.managers.installation_manager.installation_manager import InstallationManager
from prism.utilities.event_bus.local_event_bus import LocalEventBus

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
    return LocalEventBus()


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
def installation_engine(command_accessor, file_accessor, system_accessor):
    return InstallationEngine(
        command_accessor=command_accessor,
        file_accessor=file_accessor,
        system_accessor=system_accessor,
        rollback_accessor=MagicMock(),
    )


@pytest.fixture
def manager(file_accessor, system_accessor, event_bus, prisms_dir, installation_engine):
    return InstallationManager(
        config_engine=ConfigEngine(),
        installation_engine=installation_engine,
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

    def test_publishes_complete_event(self, manager, file_accessor, event_bus, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        events = []
        event_bus.subscribe("installation.complete", lambda payload: events.append(payload))
        manager.install("startup", {"name": "Bob"})
        assert len(events) == 1
        assert events[0]["package"] == "startup"
        assert events[0]["success"] is True


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

    def test_publishes_failed_event(self, manager, file_accessor, event_bus):
        file_accessor.get_package_config.side_effect = FileNotFoundError("not found")
        events = []
        event_bus.subscribe("installation.failed", lambda payload: events.append(payload))
        result = manager.install("missing", {})
        assert result.success is False
        assert len(events) == 1


# ------------------------------------------------------------------
# check_readiness (delegates to engine)
# ------------------------------------------------------------------


class TestCheckReadiness:
    def test_all_satisfied(self, manager, system_accessor):
        system_accessor.get_installed_version.return_value = "3.11"
        ok, failures = manager.check_readiness({"python_version": ">=3.8"})
        assert ok is True

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


# ------------------------------------------------------------------
# Two-phase install (privilege separation)
# ------------------------------------------------------------------


class TestTwoPhaseInstall:
    def test_skip_privileged_returns_phase_1(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {}, skip_privileged=True)
        assert result.success is True
        assert result.phase == 1

    def test_normal_install_is_phase_2(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {})
        assert result.phase == 2

    def test_normal_install_no_pending(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        result = manager.install("startup", {})
        assert result.pending_privileged == []

    def test_install_privileged_delegates(self, manager, command_accessor):
        from prism.models.installation import PrivilegedStep

        steps = [PrivilegedStep(name="docker", command="brew install docker", needs_sudo=False, platform="mac")]
        command_accessor.pkg_is_installed.return_value = False
        result = manager.install_privileged(steps, "mac")
        assert result.success is True
        assert result.phase == 2


# ------------------------------------------------------------------
# Configurable workspace (BL-010)
# ------------------------------------------------------------------


class TestConfigurableWorkspace:
    def test_custom_workspace_dir(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {"workspace_dir": "/tmp/myworkspace"})
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        assert any("/tmp/myworkspace" in p for p in paths)

    def test_tilde_expansion(self, manager, file_accessor, valid_config):
        file_accessor.get_package_config.return_value = valid_config
        manager.install("startup", {"workspace_dir": "~/development"})
        mkdir_calls = file_accessor.mkdir.call_args_list
        paths = [str(call.args[0]) for call in mkdir_calls]
        assert not any("~" in p for p in paths)

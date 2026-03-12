"""Unit tests for InstallationEngine (installation, rollback, sudo, tools, preflight)."""

from __future__ import annotations

from unittest.mock import MagicMock

from prism.engines.installation_engine._rollback import compute_rollback_plan
from prism.engines.installation_engine._tools import resolve_tools
from prism.engines.installation_engine._versions import version_satisfies
from prism.engines.installation_engine.i_installation_engine import IInstallationEngine
from prism.engines.installation_engine.installation_engine import InstallationEngine
from prism.models.installation import RollbackAction, RollbackState


def _make_engine() -> InstallationEngine:
    """Create an InstallationEngine with mock accessors."""
    return InstallationEngine(
        command_accessor=MagicMock(),
        file_accessor=MagicMock(),
        system_accessor=MagicMock(),
        rollback_accessor=MagicMock(),
    )


class TestInterfaceConformance:
    def test_implements_interface(self):
        engine = _make_engine()
        assert isinstance(engine, IInstallationEngine)


# ------------------------------------------------------------------
# Version checking (private, tested via check_requirements)
# ------------------------------------------------------------------


class TestVersionSatisfies:
    def test_gte(self):
        assert version_satisfies("3.11", ">=3.8") is True
        assert version_satisfies("3.7", ">=3.8") is False
        assert version_satisfies("3.8", ">=3.8") is True

    def test_gt(self):
        assert version_satisfies("3.9", ">3.8") is True
        assert version_satisfies("3.8", ">3.8") is False

    def test_lte(self):
        assert version_satisfies("3.8", "<=3.8") is True
        assert version_satisfies("3.9", "<=3.8") is False

    def test_lt(self):
        assert version_satisfies("3.7", "<3.8") is True
        assert version_satisfies("3.8", "<3.8") is False

    def test_eq(self):
        assert version_satisfies("3.8", "==3.8") is True
        assert version_satisfies("3.9", "==3.8") is False

    def test_unknown_format(self):
        assert version_satisfies("3.8", "latest") is True


# ------------------------------------------------------------------
# Tool resolution (private)
# ------------------------------------------------------------------


class TestResolveTools:
    def test_basic_resolution(self):
        merged = {"tools_required": ["git", "docker", "node"]}
        result = resolve_tools(merged, "mac")
        names = [t["name"] for t in result]
        assert names == ["git", "docker", "node"]

    def test_platform_filter(self):
        merged = {"tools_required": [{"name": "brew", "platforms": ["mac"]}, {"name": "git"}]}
        result = resolve_tools(merged, "linux")
        names = [t["name"] for t in result]
        assert "brew" not in names
        assert "git" in names

    def test_whitelist(self):
        merged = {"tools_required": ["git", "docker", "node"]}
        result = resolve_tools(merged, "mac", tools_selected=["git", "node"])
        names = [t["name"] for t in result]
        assert "docker" not in names

    def test_blacklist(self):
        merged = {"tools_required": ["git", "docker", "node"]}
        result = resolve_tools(merged, "mac", tools_excluded=["docker"])
        names = [t["name"] for t in result]
        assert "docker" not in names

    def test_empty_tools(self):
        result = resolve_tools({}, "mac")
        assert result == []


# ------------------------------------------------------------------
# Workspace planning (private)
# ------------------------------------------------------------------


class TestPlanWorkspace:
    def test_default_dirs(self):
        engine = _make_engine()
        result = engine._plan_workspace({})
        assert "projects" in result

    def test_config_dirs_replace_defaults(self):
        engine = _make_engine()
        result = engine._plan_workspace({}, config_dirs=["src", "infra"])
        assert "src" in result
        assert "projects" not in result

    def test_no_duplicate_dirs(self):
        engine = _make_engine()
        merged = {"workspace": {"directories": ["projects"]}}
        result = engine._plan_workspace(merged)
        assert result.count("projects") == 1


# ------------------------------------------------------------------
# Git config planning (private)
# ------------------------------------------------------------------


class TestPlanGitConfig:
    def test_basic_config(self):
        engine = _make_engine()
        user_info = {"name": "Jane", "email": "jane@co.com"}
        result = engine._plan_git_config(user_info, {})
        keys = [k for k, v in result]
        assert "user.name" in keys
        assert "user.email" in keys
        assert "init.defaultBranch" in keys

    def test_fallback_to_merged_config(self):
        engine = _make_engine()
        merged = {"git": {"user": {"name": "Config Name", "email": "config@co.com"}}}
        result = engine._plan_git_config({}, merged)
        values = {k: v for k, v in result}
        assert values["user.name"] == "Config Name"


# ------------------------------------------------------------------
# Repo clone planning (private)
# ------------------------------------------------------------------


class TestPlanRepoClones:
    def test_string_repos(self):
        engine = _make_engine()
        merged = {"repositories": ["https://github.com/org/repo.git"]}
        result = engine._plan_repo_clones(merged, "/workspace")
        assert len(result) == 1
        assert result[0]["name"] == "repo"

    def test_empty_repos(self):
        engine = _make_engine()
        result = engine._plan_repo_clones({}, "/workspace")
        assert result == []


# ------------------------------------------------------------------
# Rollback
# ------------------------------------------------------------------


class TestRollback:
    def test_compute_rollback_plan_filters(self):
        state = RollbackState(package_name="test")
        state.record(RollbackAction(action_type="file_created", target="/tmp/x"))
        state.record(RollbackAction(action_type="unknown", target="y"))
        state.record(RollbackAction(action_type="config_changed", target="z", original_value="old"))

        plan = compute_rollback_plan(state)
        types = [a.action_type for a in plan]
        assert "file_created" in types
        assert "config_changed" in types
        assert "unknown" not in types


# ------------------------------------------------------------------
# Sudo sessions
# ------------------------------------------------------------------


class TestSudoSession:
    def test_create_session(self):
        engine = _make_engine()
        session = engine.create_sudo_session()
        assert session.token
        assert session.attempts == 0

    def test_validate_fresh_session(self):
        engine = _make_engine()
        session = engine.create_sudo_session()
        assert engine.validate_sudo_session(session) is True

    def test_record_success_resets(self):
        engine = _make_engine()
        session = engine.create_sudo_session()
        session = engine.record_sudo_attempt(session, False)
        assert session.attempts == 1
        session = engine.record_sudo_attempt(session, True)
        assert session.attempts == 0

    def test_lockout_after_max_attempts(self):
        engine = _make_engine()
        session = engine.create_sudo_session()
        for _ in range(session.max_attempts):
            session = engine.record_sudo_attempt(session, False)
        assert session.is_locked is True
        assert engine.validate_sudo_session(session) is False


# ------------------------------------------------------------------
# Package source resolution
# ------------------------------------------------------------------


class TestResolvePackageSource:
    def test_local_default(self):
        engine = _make_engine()
        result = engine.resolve_package_source("my-prism")
        assert result["type"] == "local"

    def test_npm_scoped(self):
        engine = _make_engine()
        result = engine.resolve_package_source("@prism-dx/my-prism")
        assert result["type"] == "npm"

    def test_explicit_sources(self):
        engine = _make_engine()
        sources = [{"type": "npm", "registry": "https://custom.registry.com"}]
        result = engine.resolve_package_source("my-prism", sources)
        assert result["type"] == "npm"
        assert "custom.registry.com" in result["registry_url"]

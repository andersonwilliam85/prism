"""Unit tests for SetupEngine (consolidated from SetupPlan + ToolResolution + Preflight)."""

from __future__ import annotations

from prism.engines.setup_engine.setup_engine import SetupEngine
from prism.engines.setup_engine.i_setup_engine import ISetupEngine


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(SetupEngine(), ISetupEngine)


class TestPlanGitConfig:
    def test_basic_config(self):
        engine = SetupEngine()
        user_info = {"name": "Jane Doe", "email": "jane@co.com"}
        result = engine.plan_git_config(user_info, {})
        keys = [k for k, v in result]
        assert "user.name" in keys
        assert "user.email" in keys
        assert "init.defaultBranch" in keys

    def test_fallback_to_merged_config(self):
        engine = SetupEngine()
        user_info = {}
        merged = {"git": {"user": {"name": "Config Name", "email": "config@co.com"}}}
        result = engine.plan_git_config(user_info, merged)
        values = {k: v for k, v in result}
        assert values["user.name"] == "Config Name"

    def test_extra_git_config(self):
        engine = SetupEngine()
        user_info = {"name": "X", "email": "x@co.com"}
        merged = {"git": {"config": {"core.autocrlf": "true"}}}
        result = engine.plan_git_config(user_info, merged)
        keys = [k for k, v in result]
        assert "core.autocrlf" in keys


class TestPlanWorkspace:
    def test_default_dirs(self):
        engine = SetupEngine()
        result = engine.plan_workspace({})
        assert "projects" in result
        assert "experiments" in result

    def test_custom_dirs(self):
        engine = SetupEngine()
        merged = {"workspace": {"directories": ["custom", "another"]}}
        result = engine.plan_workspace(merged)
        assert "custom" in result
        assert "another" in result
        assert "projects" in result  # defaults preserved

    def test_no_duplicate_dirs(self):
        engine = SetupEngine()
        merged = {"workspace": {"directories": ["projects"]}}
        result = engine.plan_workspace(merged)
        assert result.count("projects") == 1


class TestPlanRepoClones:
    def test_string_repos(self):
        engine = SetupEngine()
        merged = {"repositories": ["https://github.com/org/repo.git"]}
        result = engine.plan_repo_clones(merged, "/home/user/workspace")
        assert len(result) == 1
        assert result[0]["name"] == "repo"
        assert result[0]["url"] == "https://github.com/org/repo.git"

    def test_dict_repos(self):
        engine = SetupEngine()
        merged = {"repositories": [{"url": "https://github.com/org/api.git", "name": "api", "path": "~/dev/api"}]}
        result = engine.plan_repo_clones(merged, "/workspace")
        assert result[0]["name"] == "api"

    def test_empty_repos(self):
        engine = SetupEngine()
        result = engine.plan_repo_clones({}, "/workspace")
        assert result == []


class TestResolveTools:
    def test_basic_resolution(self):
        engine = SetupEngine()
        merged = {"tools_required": ["git", "docker", "node"]}
        result = engine.resolve_tools(merged, "mac")
        names = [t["name"] for t in result]
        assert names == ["git", "docker", "node"]

    def test_platform_filter(self):
        engine = SetupEngine()
        merged = {
            "tools_required": [
                {"name": "brew", "platforms": ["mac"]},
                {"name": "git"},
            ]
        }
        result = engine.resolve_tools(merged, "linux")
        names = [t["name"] for t in result]
        assert "brew" not in names
        assert "git" in names

    def test_whitelist(self):
        engine = SetupEngine()
        merged = {"tools_required": ["git", "docker", "node"]}
        result = engine.resolve_tools(merged, "mac", tools_selected=["git", "node"])
        names = [t["name"] for t in result]
        assert "docker" not in names
        assert "git" in names

    def test_blacklist(self):
        engine = SetupEngine()
        merged = {"tools_required": ["git", "docker", "node"]}
        result = engine.resolve_tools(merged, "mac", tools_excluded=["docker"])
        names = [t["name"] for t in result]
        assert "docker" not in names
        assert "git" in names

    def test_empty_tools(self):
        engine = SetupEngine()
        result = engine.resolve_tools({}, "mac")
        assert result == []

    def test_legacy_tools_key(self):
        engine = SetupEngine()
        merged = {"tools": ["git"]}
        result = engine.resolve_tools(merged, "mac")
        assert len(result) == 1


class TestCheckRequirements:
    def test_all_satisfied(self):
        engine = SetupEngine()
        reqs = {"git": True, "python_version": ">=3.8"}
        installed = {"git": "2.40.1", "python": "3.11.0"}
        passed, failures = engine.check_requirements(reqs, installed)
        assert passed is True
        assert failures == []

    def test_missing_tool(self):
        engine = SetupEngine()
        reqs = {"docker": True}
        installed = {}
        passed, failures = engine.check_requirements(reqs, installed)
        assert passed is False
        assert "docker" in failures[0]

    def test_version_too_low(self):
        engine = SetupEngine()
        reqs = {"python_version": ">=3.10"}
        installed = {"python": "3.8.0"}
        passed, failures = engine.check_requirements(reqs, installed)
        assert passed is False

    def test_onboarding_version_skipped(self):
        engine = SetupEngine()
        reqs = {"onboarding_version": "2.0"}
        installed = {}
        passed, _ = engine.check_requirements(reqs, installed)
        assert passed is True


class TestVersionSatisfies:
    def test_gte(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.11", ">=3.8") is True
        assert engine.version_satisfies("3.7", ">=3.8") is False
        assert engine.version_satisfies("3.8", ">=3.8") is True

    def test_gt(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.9", ">3.8") is True
        assert engine.version_satisfies("3.8", ">3.8") is False

    def test_lte(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.8", "<=3.8") is True
        assert engine.version_satisfies("3.9", "<=3.8") is False

    def test_lt(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.7", "<3.8") is True
        assert engine.version_satisfies("3.8", "<3.8") is False

    def test_eq(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.8", "==3.8") is True
        assert engine.version_satisfies("3.9", "==3.8") is False

    def test_unknown_format(self):
        engine = SetupEngine()
        assert engine.version_satisfies("3.8", "latest") is True

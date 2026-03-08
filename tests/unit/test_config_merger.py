"""
Unit tests for ConfigMerger — hierarchical config merging engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import os  # noqa: E402

import pytest  # noqa: E402
import yaml  # noqa: E402
from config_merger import ConfigMerger, merge_configs  # noqa: E402


@pytest.mark.unit
class TestMergeConfigs:
    """Tests for the merge_configs() convenience function."""

    def test_merges_flat_configs(self):
        base = {"name": "Base", "version": "1.0"}
        override = {"version": "2.0", "author": "Test"}
        result = merge_configs(base, override)
        assert result["name"] == "Base"
        assert result["version"] == "2.0"
        assert result["author"] == "Test"

    def test_base_preserved_when_key_absent_in_override(self):
        base = {"a": 1, "b": 2, "c": 3}
        result = merge_configs(base, {"b": 99})
        assert result["a"] == 1
        assert result["b"] == 99
        assert result["c"] == 3

    def test_new_key_from_override_added(self):
        result = merge_configs({"x": 1}, {"y": 2})
        assert result["x"] == 1
        assert result["y"] == 2

    def test_none_override_replaces_value(self):
        result = merge_configs({"field": "value"}, {"field": None})
        assert result["field"] is None

    def test_string_override_replaces_string(self):
        result = merge_configs({"color": "blue"}, {"color": "red"})
        assert result["color"] == "red"

    def test_integer_override(self):
        result = merge_configs({"count": 5}, {"count": 10})
        assert result["count"] == 10

    def test_empty_base(self):
        result = merge_configs({}, {"key": "value"})
        assert result["key"] == "value"

    def test_empty_override(self):
        result = merge_configs({"key": "value"}, {})
        assert result["key"] == "value"

    def test_both_empty(self):
        result = merge_configs({}, {})
        assert result == {}


@pytest.mark.unit
class TestDictMerging:
    """Tests for nested dict deep merging."""

    def test_nested_dicts_deep_merge(self):
        base = {"package": {"name": "test", "settings": {"debug": False}}}
        override = {"package": {"settings": {"debug": True, "verbose": True}}}
        result = merge_configs(base, override)
        assert result["package"]["name"] == "test"
        assert result["package"]["settings"]["debug"] is True
        assert result["package"]["settings"]["verbose"] is True

    def test_three_level_deep_merge(self):
        base = {"a": {"b": {"c": {"field": "base"}}}}
        override = {"a": {"b": {"c": {"field": "override", "extra": "new"}}}}
        result = merge_configs(base, override)
        assert result["a"]["b"]["c"]["field"] == "override"
        assert result["a"]["b"]["c"]["extra"] == "new"

    def test_sibling_keys_preserved_in_deep_merge(self):
        base = {
            "env": {
                "proxy": {"http": "http://proxy:8080"},
                "maven": {"url": "https://maven.example.com"},
            }
        }
        override = {"env": {"npm": {"registry": "https://npm.example.com"}}}
        result = merge_configs(base, override)
        assert result["env"]["proxy"]["http"] == "http://proxy:8080"
        assert result["env"]["maven"]["url"] == "https://maven.example.com"
        assert result["env"]["npm"]["registry"] == "https://npm.example.com"

    def test_dict_override_replaces_scalar(self):
        base = {"key": "string_value"}
        override = {"key": {"nested": "dict"}}
        result = merge_configs(base, override)
        assert result["key"] == {"nested": "dict"}

    def test_scalar_override_replaces_dict(self):
        base = {"key": {"nested": "dict"}}
        override = {"key": "flat_value"}
        result = merge_configs(base, override)
        assert result["key"] == "flat_value"


@pytest.mark.unit
class TestListMerging:
    """Tests for list merge strategies."""

    def test_tools_required_union_merge(self):
        """tools_required uses union strategy — no duplicates."""
        base = {"tools_required": ["git", "docker", "kubectl"]}
        override = {"tools_required": ["terraform", "docker"]}  # docker is duplicate
        result = merge_configs(base, override)
        tools = result["tools_required"]
        assert "git" in tools
        assert "kubectl" in tools
        assert "terraform" in tools
        assert tools.count("docker") == 1  # union deduplicates

    def test_unknown_list_key_uses_override(self):
        """Unknown list keys use override strategy."""
        base = {"arbitrary_list": [1, 2, 3]}
        override = {"arbitrary_list": [4, 5]}
        result = merge_configs(base, override)
        # Override strategy: last wins
        assert result["arbitrary_list"] == [4, 5]

    def test_resources_append_strategy(self):
        """resources uses append strategy — keeps all in order."""
        merger = ConfigMerger()
        base = {"resources": [{"name": "A"}, {"name": "B"}]}
        overlay = {"resources": [{"name": "C"}]}
        result = merger._merge_level(base, overlay, "test")
        assert len(result["resources"]) == 3

    def test_empty_list_in_base(self):
        base = {"tools_required": []}
        override = {"tools_required": ["git"]}
        result = merge_configs(base, override)
        assert "git" in result["tools_required"]

    def test_empty_list_in_override(self):
        base = {"tools_required": ["git", "docker"]}
        override = {"tools_required": []}
        result = merge_configs(base, override)
        # With union: base + empty = base values retained
        # (set(["git","docker"] + []) = {"git","docker"})
        assert "git" in result["tools_required"]


@pytest.mark.unit
class TestConfigMergerClass:
    """Tests for ConfigMerger class directly."""

    def test_initializes_with_default_rules(self):
        merger = ConfigMerger()
        assert merger is not None
        assert merger.rules is not None
        assert "merge_strategy" in merger.rules

    def test_default_rules_have_array_strategies(self):
        merger = ConfigMerger()
        arrays = merger.rules["merge_strategy"]["arrays"]
        assert "tools_selected" in arrays
        assert "resources" in arrays

    def test_default_rules_have_object_strategies(self):
        merger = ConfigMerger()
        objects = merger.rules["merge_strategy"]["objects"]
        assert "environment" in objects
        assert "git" in objects

    def test_merge_level_new_key(self):
        merger = ConfigMerger()
        result = merger._merge_level({}, {"new_key": "value"}, "base")
        assert result["new_key"] == "value"

    def test_merge_level_override_existing(self):
        merger = ConfigMerger()
        result = merger._merge_level({"key": "old"}, {"key": "new"}, "role")
        assert result["key"] == "new"

    def test_merge_level_preserves_base_not_in_overlay(self):
        merger = ConfigMerger()
        result = merger._merge_level({"a": 1, "b": 2}, {"b": 99}, "team")
        assert result["a"] == 1
        assert result["b"] == 99

    def test_get_merge_strategy_known_key(self):
        merger = ConfigMerger()
        strategy = merger._get_merge_strategy("environment")
        assert strategy == "deep_merge"

    def test_get_merge_strategy_unknown_key(self):
        merger = ConfigMerger()
        strategy = merger._get_merge_strategy("unknown_key_xyz")
        assert strategy in {"override", "deep_merge", "union", "append"}

    def test_get_array_strategy_tools_selected(self):
        merger = ConfigMerger()
        strategy = merger._get_array_strategy("tools_selected")
        assert strategy == "union"

    def test_get_array_strategy_resources(self):
        merger = ConfigMerger()
        strategy = merger._get_array_strategy("resources")
        assert strategy == "append"

    def test_get_array_strategy_unknown(self):
        merger = ConfigMerger()
        strategy = merger._get_array_strategy("unknown_array_xyz")
        assert strategy == "override"

    def test_deep_merge_dicts(self):
        merger = ConfigMerger()
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        overlay = {"a": {"y": 99, "z": 4}, "c": 5}
        result = merger._deep_merge_dicts(base, overlay)
        assert result["a"]["x"] == 1
        assert result["a"]["y"] == 99
        assert result["a"]["z"] == 4
        assert result["b"] == 3
        assert result["c"] == 5

    def test_user_only_strategy_respected(self):
        """user_only fields can only be set by user level."""
        merger = ConfigMerger()
        base = {"career": {"goal": "original"}}
        overlay = {"career": {"goal": "override_attempt"}}
        # Non-user level should not override user_only fields
        result = merger._merge_value("career", base["career"], overlay["career"], "team")
        assert result["goal"] == "original"

    def test_user_only_strategy_user_level(self):
        """user_only fields ARE overridden at user level."""
        merger = ConfigMerger()
        base_val = {"goal": "original"}
        overlay_val = {"goal": "user_set"}
        result = merger._merge_value("career", base_val, overlay_val, "user")
        assert result["goal"] == "user_set"

    def test_git_override_strategy(self):
        """git uses override strategy — later layer completely replaces."""
        merger = ConfigMerger()
        base_val = {"user": {"name": "Base User", "email": "base@example.com"}}
        overlay_val = {"user": {"name": "Override User", "email": "override@example.com"}}
        result = merger._merge_value("git", base_val, overlay_val, "role")
        assert result["user"]["name"] == "Override User"

    def test_load_merged_config_with_files(self, tmp_path):
        base_yaml = tmp_path / "base.yaml"
        team_yaml = tmp_path / "team.yaml"
        base_yaml.write_text(
            yaml.dump(
                {
                    "company": {"name": "ACME"},
                    "tools_required": ["git", "docker"],
                }
            )
        )
        team_yaml.write_text(
            yaml.dump(
                {
                    "tools_required": ["kubectl"],
                    "team": {"name": "Platform"},
                }
            )
        )
        merger = ConfigMerger()
        result = merger.load_merged_config(
            company=str(base_yaml),
            team=str(team_yaml),
        )
        assert result["company"]["name"] == "ACME"
        assert "git" in result["tools_required"]
        assert "kubectl" in result["tools_required"]
        assert result["team"]["name"] == "Platform"

    def test_load_merged_config_missing_file(self, tmp_path):
        """Missing config files are silently skipped."""
        merger = ConfigMerger()
        result = merger.load_merged_config(
            company=str(tmp_path / "nonexistent.yaml"),
        )
        assert result == {}

    def test_load_merged_config_all_none(self):
        merger = ConfigMerger()
        result = merger.load_merged_config()
        assert result == {}


@pytest.mark.unit
class TestEnvVarSubstitution:
    """Tests for ${VAR} and ${VAR:-default} substitution."""

    def setup_method(self):
        os.environ["PRISM_TEST_VAR"] = "test_value"
        os.environ.pop("PRISM_UNSET_VAR", None)

    def teardown_method(self):
        os.environ.pop("PRISM_TEST_VAR", None)

    def test_substitutes_env_var(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"key": "${PRISM_TEST_VAR}"})
        assert result["key"] == "test_value"

    def test_default_used_when_var_unset(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"key": "${PRISM_UNSET_VAR:-my_default}"})
        assert result["key"] == "my_default"

    def test_env_var_overrides_default(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"key": "${PRISM_TEST_VAR:-fallback}"})
        assert result["key"] == "test_value"

    def test_substitution_in_nested_dict(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"git": {"user": {"email": "${PRISM_TEST_VAR}@example.com"}}})
        assert result["git"]["user"]["email"] == "test_value@example.com"

    def test_substitution_in_list(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"items": ["${PRISM_TEST_VAR}", "literal"]})
        assert result["items"][0] == "test_value"
        assert result["items"][1] == "literal"

    def test_non_string_values_unchanged(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"count": 42, "flag": True, "nothing": None})
        assert result["count"] == 42
        assert result["flag"] is True
        assert result["nothing"] is None

    def test_multiple_vars_in_one_string(self):
        merger = ConfigMerger()
        result = merger._substitute_env_vars({"url": "https://${PRISM_TEST_VAR}.example.com/${PRISM_UNSET_VAR:-path}"})
        assert result["url"] == "https://test_value.example.com/path"


@pytest.mark.unit
class TestMultiLevelMerging:
    """Tests for realistic multi-tier sub-prism merging."""

    def test_three_tier_tools_union(self):
        """Base + division + role tools all union together."""
        merger = ConfigMerger()
        base = {"tools_required": ["git", "docker"]}
        division = {"tools_required": ["vscode", "docker"]}  # docker duplicate
        role = {"tools_required": ["terraform", "ansible"]}

        merged = merger._merge_level({}, base, "base")
        merged = merger._merge_level(merged, division, "division")
        merged = merger._merge_level(merged, role, "role")

        tools = merged["tools_required"]
        assert "git" in tools
        assert "vscode" in tools
        assert "terraform" in tools
        assert "ansible" in tools
        assert tools.count("docker") == 1  # deduplicated

    def test_later_tier_extends_environment(self):
        merger = ConfigMerger()
        base = {"environment": {"proxy": {"http": "http://proxy:8080"}, "vpn": {"required": True}}}
        role = {"environment": {"npm": {"registry": "https://npm.example.com"}}}

        merged = merger._merge_level({}, base, "base")
        merged = merger._merge_level(merged, role, "role")

        assert merged["environment"]["proxy"]["http"] == "http://proxy:8080"
        assert merged["environment"]["vpn"]["required"] is True
        assert merged["environment"]["npm"]["registry"] == "https://npm.example.com"

    def test_new_keys_accumulate_across_tiers(self):
        merger = ConfigMerger()
        t1 = {"company": {"name": "ACME"}}
        t2 = {"division": {"id": "tech"}}
        t3 = {"role": {"id": "devops"}}

        merged = merger._merge_level({}, t1, "base")
        merged = merger._merge_level(merged, t2, "division")
        merged = merger._merge_level(merged, t3, "role")

        assert merged["company"]["name"] == "ACME"
        assert merged["division"]["id"] == "tech"
        assert merged["role"]["id"] == "devops"

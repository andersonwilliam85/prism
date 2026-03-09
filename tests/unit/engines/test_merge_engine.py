"""Unit tests for MergeEngine (renamed from ConfigMergeEngine)."""

from __future__ import annotations

from prism.engines.merge_engine.merge_engine import MergeEngine
from prism.engines.merge_engine.i_merge_engine import IMergeEngine


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(MergeEngine(), IMergeEngine)


class TestMerge:
    def test_disjoint_keys(self):
        engine = MergeEngine()
        result = engine.merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_override_primitive(self):
        engine = MergeEngine()
        result = engine.merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_deep_merge_dicts(self):
        engine = MergeEngine()
        base = {"environment": {"proxy": {"http": "http://old"}}}
        override = {"environment": {"proxy": {"https": "https://new"}, "debug": True}}
        result = engine.merge(base, override)
        assert result["environment"]["proxy"]["http"] == "http://old"
        assert result["environment"]["proxy"]["https"] == "https://new"
        assert result["environment"]["debug"] is True

    def test_array_union_tools_required(self):
        engine = MergeEngine()
        base = {"tools_required": ["git", "docker"]}
        override = {"tools_required": ["docker", "node"]}
        result = engine.merge(base, override)
        assert set(result["tools_required"]) == {"git", "docker", "node"}

    def test_array_append_repositories(self):
        engine = MergeEngine()
        base = {"repositories": ["repo1"]}
        override = {"repositories": ["repo2"]}
        result = engine.merge(base, override)
        assert result["repositories"] == ["repo1", "repo2"]

    def test_array_override_unknown_key(self):
        engine = MergeEngine()
        base = {"custom_list": [1, 2]}
        override = {"custom_list": [3, 4]}
        result = engine.merge(base, override)
        assert result["custom_list"] == [3, 4]

    def test_git_override_strategy(self):
        engine = MergeEngine()
        base = {"git": {"user": {"name": "Old"}}}
        override = {"git": {"user": {"name": "New"}}}
        result = engine.merge(base, override)
        assert result["git"] == {"user": {"name": "New"}}

    def test_user_only_strategy(self):
        engine = MergeEngine()
        base = {"career": {"goal": "original"}}
        override = {"career": {"goal": "overridden"}}
        result = engine.merge(base, override)
        assert result["career"]["goal"] == "original"

    def test_does_not_mutate_inputs(self):
        engine = MergeEngine()
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        engine.merge(base, override)
        assert "c" not in base["a"]


class TestMergeTiers:
    def test_sequential_merge(self):
        engine = MergeEngine()
        base = {"tools_required": ["git"]}
        tiers = [
            {"tools_required": ["docker"]},
            {"tools_required": ["node"]},
        ]
        result = engine.merge_tiers(base, tiers)
        assert set(result["tools_required"]) == {"git", "docker", "node"}

    def test_empty_tiers(self):
        engine = MergeEngine()
        base = {"key": "value"}
        result = engine.merge_tiers(base, [])
        assert result == {"key": "value"}

    def test_tier_adds_new_keys(self):
        engine = MergeEngine()
        base = {"a": 1}
        tiers = [{"b": 2}, {"c": 3}]
        result = engine.merge_tiers(base, tiers)
        assert result == {"a": 1, "b": 2, "c": 3}


class TestCustomRules:
    def test_custom_array_strategy(self):
        rules = {
            "merge_strategy": {
                "arrays": {"my_list": "append"},
                "objects": {},
                "conflicts": {"default": "override"},
            }
        }
        engine = MergeEngine(rules=rules)
        result = engine.merge({"my_list": [1]}, {"my_list": [2]})
        assert result["my_list"] == [1, 2]

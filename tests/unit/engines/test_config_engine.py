"""Unit tests for ConfigEngine (validation, merge, hierarchy)."""

from __future__ import annotations

from prism.engines.config_engine.config_engine import ConfigEngine
from prism.engines.config_engine.i_config_engine import IConfigEngine
from prism.models.package_info import UserField


class TestInterfaceConformance:
    def test_implements_interface(self):
        assert isinstance(ConfigEngine(), IConfigEngine)


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------


class TestValidate:
    def test_valid_config(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "test", "version": "1.0", "description": "A test"},
            "bundled_prisms": {"base": [{"id": "base", "config": "base.yaml"}]},
            "user_info_fields": [{"id": "name", "label": "Name", "type": "text"}],
        }
        valid, errors, warnings = engine.validate(config)
        assert valid is True
        assert errors == []

    def test_empty_config(self):
        engine = ConfigEngine()
        valid, errors, _ = engine.validate({})
        assert valid is False
        assert "Config is empty" in errors[0]

    def test_missing_package(self):
        engine = ConfigEngine()
        valid, errors, _ = engine.validate({"bundled_prisms": {}})
        assert valid is False
        assert any("package" in e for e in errors)

    def test_missing_required_fields(self):
        engine = ConfigEngine()
        config = {"package": {"name": "test"}}
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("version" in e for e in errors)

    def test_empty_required_field(self):
        engine = ConfigEngine()
        config = {"package": {"name": "", "version": "1.0", "description": "x"}}
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("Empty" in e for e in errors)

    def test_no_bundled_prisms_warning(self):
        engine = ConfigEngine()
        config = {"package": {"name": "x", "version": "1", "description": "x"}}
        valid, _, warnings = engine.validate(config)
        assert valid is True
        assert any("bundled_prisms" in w for w in warnings)

    def test_theme_must_be_string(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "prism_config": {"theme": 123},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("theme" in e for e in errors)

    def test_bundled_prisms_validation(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "bundled_prisms": {"base": [{"no_id": True}]},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("id" in e for e in errors)

    def test_user_info_fields_unknown_type(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "user_info_fields": [{"id": "x", "label": "X", "type": "invalid_type"}],
        }
        _, _, warnings = engine.validate(config)
        assert any("unknown type" in w for w in warnings)

    def test_metadata_tags_must_be_list(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "x", "version": "1", "description": "x"},
            "metadata": {"tags": "not-a-list"},
        }
        valid, errors, _ = engine.validate(config)
        assert valid is False
        assert any("tags" in e for e in errors)


# ------------------------------------------------------------------
# Merge
# ------------------------------------------------------------------


class TestMerge:
    def test_disjoint_keys(self):
        engine = ConfigEngine()
        result = engine.merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_override_primitive(self):
        engine = ConfigEngine()
        result = engine.merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_deep_merge_dicts(self):
        engine = ConfigEngine()
        base = {"environment": {"proxy": {"http": "http://old"}}}
        override = {"environment": {"proxy": {"https": "https://new"}, "debug": True}}
        result = engine.merge(base, override)
        assert result["environment"]["proxy"]["http"] == "http://old"
        assert result["environment"]["proxy"]["https"] == "https://new"
        assert result["environment"]["debug"] is True

    def test_array_union_tools_required(self):
        engine = ConfigEngine()
        base = {"tools_required": ["git", "docker"]}
        override = {"tools_required": ["docker", "node"]}
        result = engine.merge(base, override)
        assert set(result["tools_required"]) == {"git", "docker", "node"}

    def test_array_append_repositories(self):
        engine = ConfigEngine()
        base = {"repositories": ["repo1"]}
        override = {"repositories": ["repo2"]}
        result = engine.merge(base, override)
        assert result["repositories"] == ["repo1", "repo2"]

    def test_array_override_unknown_key(self):
        engine = ConfigEngine()
        base = {"custom_list": [1, 2]}
        override = {"custom_list": [3, 4]}
        result = engine.merge(base, override)
        assert result["custom_list"] == [3, 4]

    def test_git_override_strategy(self):
        engine = ConfigEngine()
        base = {"git": {"user": {"name": "Old"}}}
        override = {"git": {"user": {"name": "New"}}}
        result = engine.merge(base, override)
        assert result["git"] == {"user": {"name": "New"}}

    def test_user_only_strategy(self):
        engine = ConfigEngine()
        base = {"career": {"goal": "original"}}
        override = {"career": {"goal": "overridden"}}
        result = engine.merge(base, override)
        assert result["career"]["goal"] == "original"

    def test_does_not_mutate_inputs(self):
        engine = ConfigEngine()
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        engine.merge(base, override)
        assert "c" not in base["a"]


class TestMergeTiers:
    def test_sequential_merge(self):
        engine = ConfigEngine()
        base = {"tools_required": ["git"]}
        tiers = [{"tools_required": ["docker"]}, {"tools_required": ["node"]}]
        result = engine.merge_tiers(base, tiers)
        assert set(result["tools_required"]) == {"git", "docker", "node"}

    def test_empty_tiers(self):
        engine = ConfigEngine()
        base = {"key": "value"}
        result = engine.merge_tiers(base, [])
        assert result == {"key": "value"}

    def test_tier_adds_new_keys(self):
        engine = ConfigEngine()
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
        engine = ConfigEngine(rules=rules)
        result = engine.merge({"my_list": [1]}, {"my_list": [2]})
        assert result["my_list"] == [1, 2]


# ------------------------------------------------------------------
# Prepare (validate + merge)
# ------------------------------------------------------------------


class TestPrepare:
    def test_valid_with_tiers(self):
        engine = ConfigEngine()
        config = {
            "package": {"name": "test", "version": "1.0", "description": "A test"},
            "bundled_prisms": {"base": [{"id": "base", "config": "base.yaml"}]},
        }
        tiers = [{"tools_required": ["git"]}]
        valid, merged, errors, _ = engine.prepare(config, tiers)
        assert valid is True
        assert "tools_required" in merged

    def test_invalid_config(self):
        engine = ConfigEngine()
        valid, merged, errors, _ = engine.prepare({})
        assert valid is False
        assert merged == {}


# ------------------------------------------------------------------
# Field hierarchy
# ------------------------------------------------------------------


class TestFieldHierarchy:
    def test_resolve_dependency_order(self):
        engine = ConfigEngine()
        fields = [
            UserField(id="team", label="Team", type="select", depends_on="department"),
            UserField(id="department", label="Department", type="select"),
            UserField(id="name", label="Name", type="text"),
        ]
        ordered = engine.resolve_dependency_order(fields)
        ids = [f.id for f in ordered]
        assert ids.index("department") < ids.index("team")

    def test_filter_options_with_option_map(self):
        engine = ConfigEngine()
        field = UserField(
            id="team",
            label="Team",
            type="select",
            options=["A", "B", "C"],
            option_map={"Engineering": ["A", "B"], "Sales": ["C"]},
        )
        assert engine.filter_options(field, "Engineering") == ["A", "B"]
        assert engine.filter_options(field, "Sales") == ["C"]
        assert engine.filter_options(field, "Unknown") == ["A", "B", "C"]

    def test_filter_options_no_map(self):
        engine = ConfigEngine()
        field = UserField(id="team", label="Team", type="select", options=["A", "B"])
        assert engine.filter_options(field, "anything") == ["A", "B"]

    def test_get_dependent_fields(self):
        engine = ConfigEngine()
        fields = [
            UserField(id="department", label="Dept", type="select"),
            UserField(id="team", label="Team", type="select", depends_on="department"),
            UserField(id="role", label="Role", type="select", depends_on="department"),
            UserField(id="name", label="Name", type="text"),
        ]
        deps = engine.get_dependent_fields("department", fields)
        dep_ids = [f.id for f in deps]
        assert "team" in dep_ids
        assert "role" in dep_ids
        assert "name" not in dep_ids

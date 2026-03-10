"""Unit tests for HierarchyEngine — cascading field dependencies."""

from __future__ import annotations

import pytest

from prism.engines.hierarchy_engine.hierarchy_engine import HierarchyEngine
from prism.models.package_info import UserField


@pytest.fixture
def engine():
    return HierarchyEngine()


@pytest.fixture
def cascading_fields():
    return [
        UserField(id="name", label="Name", type="text", required=True),
        UserField(
            id="division",
            label="Division",
            type="select",
            options=["Technology", "Digital", "Data & Analytics"],
        ),
        UserField(
            id="role",
            label="Role",
            type="select",
            depends_on="division",
            options=["Software Engineer", "DevOps Engineer", "Data Engineer"],
            option_map={
                "Technology": ["Software Engineer", "DevOps Engineer"],
                "Digital": ["Software Engineer"],
                "Data & Analytics": ["Data Engineer"],
            },
        ),
        UserField(
            id="team",
            label="Team",
            type="select",
            depends_on="role",
            options=["Alpha", "Beta", "Gamma"],
            option_map={
                "Software Engineer": ["Alpha", "Beta"],
                "DevOps Engineer": ["Gamma"],
            },
        ),
    ]


class TestFilterOptions:
    def test_filters_by_parent_value(self, engine, cascading_fields):
        role_field = cascading_fields[2]
        filtered = engine.filter_options(role_field, "Technology")
        assert filtered == ["Software Engineer", "DevOps Engineer"]

    def test_returns_all_options_for_unknown_parent(self, engine, cascading_fields):
        role_field = cascading_fields[2]
        filtered = engine.filter_options(role_field, "Unknown")
        assert filtered == role_field.options

    def test_returns_all_options_when_no_parent_value(self, engine, cascading_fields):
        role_field = cascading_fields[2]
        filtered = engine.filter_options(role_field, "")
        assert filtered == role_field.options

    def test_returns_options_when_no_option_map(self, engine, cascading_fields):
        division_field = cascading_fields[1]
        filtered = engine.filter_options(division_field, "anything")
        assert filtered == division_field.options

    def test_filters_nested_dependency(self, engine, cascading_fields):
        team_field = cascading_fields[3]
        filtered = engine.filter_options(team_field, "DevOps Engineer")
        assert filtered == ["Gamma"]


class TestResolveDependencyOrder:
    def test_parents_before_children(self, engine, cascading_fields):
        ordered = engine.resolve_dependency_order(cascading_fields)
        ids = [f.id for f in ordered]
        assert ids.index("division") < ids.index("role")
        assert ids.index("role") < ids.index("team")

    def test_non_dependent_fields_come_first(self, engine, cascading_fields):
        ordered = engine.resolve_dependency_order(cascading_fields)
        ids = [f.id for f in ordered]
        assert ids.index("name") < ids.index("role")

    def test_preserves_all_fields(self, engine, cascading_fields):
        ordered = engine.resolve_dependency_order(cascading_fields)
        assert len(ordered) == len(cascading_fields)

    def test_handles_no_dependencies(self, engine):
        fields = [
            UserField(id="a", label="A"),
            UserField(id="b", label="B"),
        ]
        ordered = engine.resolve_dependency_order(fields)
        assert [f.id for f in ordered] == ["a", "b"]

    def test_handles_empty_list(self, engine):
        assert engine.resolve_dependency_order([]) == []


class TestGetDependentFields:
    def test_finds_direct_dependents(self, engine, cascading_fields):
        deps = engine.get_dependent_fields("division", cascading_fields)
        assert len(deps) == 1
        assert deps[0].id == "role"

    def test_no_dependents(self, engine, cascading_fields):
        deps = engine.get_dependent_fields("team", cascading_fields)
        assert deps == []

    def test_nonexistent_field(self, engine, cascading_fields):
        deps = engine.get_dependent_fields("nonexistent", cascading_fields)
        assert deps == []

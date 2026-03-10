"""Unit tests for ThemeEngine — theme resolution, validation, discovery."""

from __future__ import annotations

import pytest

from prism.engines.theme_engine.theme_engine import BUILT_IN_THEMES, DEFAULT_THEME, ThemeEngine
from prism.models.prism_config import ThemeDefinition


@pytest.fixture
def engine():
    return ThemeEngine()


class TestBuiltInThemes:
    def test_five_built_in_themes(self, engine):
        ids = engine.built_in_theme_ids()
        assert len(ids) == 5
        assert set(ids) == {"ocean", "purple", "forest", "sunset", "midnight"}

    def test_built_in_themes_have_gradients(self):
        for t in BUILT_IN_THEMES:
            assert t.gradient_1, f"{t.id} missing gradient_1"
            assert t.gradient_2, f"{t.id} missing gradient_2"


class TestResolveTheme:
    def test_resolves_valid_theme(self, engine):
        available = ["ocean", "purple", "forest"]
        assert engine.resolve_theme("purple", available) == "purple"

    def test_falls_back_on_invalid_theme(self, engine):
        available = ["ocean", "purple"]
        assert engine.resolve_theme("nonexistent", available) == DEFAULT_THEME

    def test_falls_back_on_empty_available(self, engine):
        assert engine.resolve_theme("ocean", []) == DEFAULT_THEME

    def test_resolves_custom_theme(self, engine):
        available = ["ocean", "corporate-blue"]
        assert engine.resolve_theme("corporate-blue", available) == "corporate-blue"


class TestListAvailableThemes:
    def test_returns_all_built_ins_by_default(self, engine):
        themes = engine.list_available_themes()
        assert len(themes) == 5

    def test_filters_by_theme_options(self, engine):
        themes = engine.list_available_themes(theme_options=["ocean", "midnight"])
        assert len(themes) == 2
        assert [t.id for t in themes] == ["ocean", "midnight"]

    def test_ignores_unknown_theme_options(self, engine):
        themes = engine.list_available_themes(theme_options=["ocean", "nonexistent"])
        assert len(themes) == 1
        assert themes[0].id == "ocean"

    def test_appends_custom_themes(self, engine):
        custom = [
            ThemeDefinition(
                id="corporate",
                name="Corporate Blue",
                gradient_1="#003366",
                gradient_2="#336699",
            )
        ]
        themes = engine.list_available_themes(custom_themes=custom)
        assert len(themes) == 6
        assert themes[-1].id == "corporate"

    def test_filters_and_appends_custom(self, engine):
        custom = [ThemeDefinition(id="brand", name="Brand")]
        themes = engine.list_available_themes(
            theme_options=["ocean"],
            custom_themes=custom,
        )
        assert len(themes) == 2
        assert themes[0].id == "ocean"
        assert themes[1].id == "brand"

    def test_empty_options_returns_all_built_ins(self, engine):
        themes = engine.list_available_themes(theme_options=[])
        assert len(themes) == 5


class TestValidateTheme:
    def test_valid_theme(self, engine):
        assert engine.validate_theme("ocean", ["ocean", "purple"]) is True

    def test_invalid_theme(self, engine):
        assert engine.validate_theme("nope", ["ocean", "purple"]) is False

    def test_custom_theme_valid(self, engine):
        assert engine.validate_theme("brand", ["ocean", "brand"]) is True

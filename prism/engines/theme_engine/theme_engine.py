"""ThemeEngine — pure logic for theme resolution and discovery.

No I/O. All theme definitions are data, not file reads.
"""

from __future__ import annotations

from prism.models.prism_config import ThemeDefinition

BUILT_IN_THEMES: list[ThemeDefinition] = [
    ThemeDefinition(
        id="ocean",
        name="Ocean Blue",
        gradient_1="#0093E9",
        gradient_2="#80D0C7",
        gradient_3="#13547a",
        gradient_4="#009ffd",
        gradient_5="#2a2a72",
    ),
    ThemeDefinition(
        id="purple",
        name="Purple Haze",
        gradient_1="#667eea",
        gradient_2="#764ba2",
        gradient_3="#f093fb",
        gradient_4="#4facfe",
        gradient_5="#00f2fe",
    ),
    ThemeDefinition(
        id="forest",
        name="Forest Green",
        gradient_1="#134E5E",
        gradient_2="#71B280",
        gradient_3="#56ab2f",
        gradient_4="#a8e063",
        gradient_5="#0f9b0f",
    ),
    ThemeDefinition(
        id="sunset",
        name="Sunset Orange",
        gradient_1="#f12711",
        gradient_2="#f5af19",
        gradient_3="#ff6a00",
        gradient_4="#ee0979",
        gradient_5="#ff512f",
    ),
    ThemeDefinition(
        id="midnight",
        name="Midnight Dark",
        gradient_1="#2c3e50",
        gradient_2="#3498db",
        gradient_3="#34495e",
        gradient_4="#2980b9",
        gradient_5="#1abc9c",
    ),
]

DEFAULT_THEME = "ocean"

_BUILT_IN_BY_ID = {t.id: t for t in BUILT_IN_THEMES}


class ThemeEngine:
    """Pure-logic theme engine — no I/O."""

    def resolve_theme(self, theme_name: str, available: list[str]) -> str:
        """Return theme_name if it's in available list, else DEFAULT_THEME."""
        if theme_name in available:
            return theme_name
        return DEFAULT_THEME

    def list_available_themes(
        self,
        theme_options: list[str] | None = None,
        custom_themes: list[ThemeDefinition] | None = None,
    ) -> list[ThemeDefinition]:
        """Return available themes.

        If theme_options is provided, filter built-ins to only those IDs.
        Custom themes are always appended.
        """
        if theme_options:
            themes = [_BUILT_IN_BY_ID[tid] for tid in theme_options if tid in _BUILT_IN_BY_ID]
        else:
            themes = list(BUILT_IN_THEMES)

        if custom_themes:
            themes.extend(custom_themes)

        return themes

    def validate_theme(self, theme_name: str, available: list[str]) -> bool:
        """Check if theme_name is in the available list."""
        return theme_name in available

    def built_in_theme_ids(self) -> list[str]:
        """Return IDs of all built-in themes."""
        return [t.id for t in BUILT_IN_THEMES]

"""IThemeEngine — theme resolution, validation, and discovery.

Volatility: low — theme schema is stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.prism_config import ThemeDefinition


@runtime_checkable
class IThemeEngine(Protocol):
    def resolve_theme(self, theme_name: str, available: list[str]) -> str:
        """Return theme_name if valid, else fall back to default."""
        ...

    def list_available_themes(
        self,
        theme_options: list[str] | None = None,
        custom_themes: list[ThemeDefinition] | None = None,
    ) -> list[ThemeDefinition]:
        """Return full list of available themes (built-in + custom)."""
        ...

    def validate_theme(self, theme_name: str, available: list[str]) -> bool:
        """Check if theme_name is a known theme."""
        ...

    def built_in_theme_ids(self) -> list[str]:
        """Return IDs of all built-in themes."""
        ...

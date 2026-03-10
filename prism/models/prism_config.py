"""Prism configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BrandingConfig:
    name: str = ""
    tagline: str = ""
    logo_text: str = ""
    logo_icon: str = ""
    page_title: str = ""
    header_title: str = ""
    header_subtitle: str = ""
    favicon_emoji: str = ""


@dataclass
class ThemeDefinition:
    """A single theme — built-in or custom."""

    id: str
    name: str
    gradient_1: str = ""
    gradient_2: str = ""
    gradient_3: str = ""
    gradient_4: str = ""
    gradient_5: str = ""


@dataclass
class PrismConfig:
    theme: str = "ocean"
    theme_options: list[str] = field(default_factory=list)
    default_theme: str = "ocean"
    custom_themes: list[ThemeDefinition] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    npm_registry: str = ""
    unpkg_url: str = ""
    proxies: dict[str, str] = field(default_factory=dict)
    branding: BrandingConfig = field(default_factory=BrandingConfig)

"""Prism configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BrandingConfig:
    logo_text: str = ""
    logo_icon: str = ""
    page_title: str = ""
    header_title: str = ""
    header_subtitle: str = ""
    favicon_emoji: str = ""


@dataclass
class PrismConfig:
    theme: str = "ocean"
    sources: list[str] = field(default_factory=list)
    npm_registry: str = ""
    unpkg_url: str = ""
    proxies: dict[str, str] = field(default_factory=dict)
    branding: BrandingConfig = field(default_factory=BrandingConfig)

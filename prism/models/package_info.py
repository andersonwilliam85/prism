"""Package metadata models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserField:
    id: str
    label: str
    type: str = "text"
    required: bool = False
    placeholder: str = ""
    options: list[str] = field(default_factory=list)


@dataclass
class TierInfo:
    id: str
    name: str
    required: bool = False


@dataclass
class PackageInfo:
    name: str
    display_name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    package_type: str = "prism"
    has_tiers: bool = False
    has_tools: bool = False
    path: str = ""

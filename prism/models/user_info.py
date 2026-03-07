"""User info model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserInfo:
    """User-supplied info collected during installation."""

    values: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: str = "") -> str:
        return self.values.get(key, default)

    def __getitem__(self, key: str) -> str:
        return self.values[key]

    def __contains__(self, key: str) -> bool:
        return key in self.values

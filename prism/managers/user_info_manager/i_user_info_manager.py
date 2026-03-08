"""IUserInfoManager — orchestrates user info schema retrieval and input validation.

Volatility: medium — field definitions and validation rules evolve
with UX changes and new field types.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.package_info import UserField


@runtime_checkable
class IUserInfoManager(Protocol):
    def get_fields(self, package_name: str) -> list[UserField]: ...

    def get_defaults(self, package_name: str) -> dict[str, str]: ...

    def validate(self, data: dict[str, str], fields: list[UserField]) -> tuple[bool, list[str]]: ...

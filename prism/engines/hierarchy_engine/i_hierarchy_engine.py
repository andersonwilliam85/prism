"""IHierarchyEngine — cascading field dependency resolution.

Volatility: low — field dependency schema is stable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from prism.models.package_info import UserField


@runtime_checkable
class IHierarchyEngine(Protocol):
    def filter_options(self, field: UserField, parent_value: str) -> list[str]:
        """Return filtered options for a dependent field given parent value."""
        ...

    def resolve_dependency_order(self, fields: list[UserField]) -> list[UserField]:
        """Sort fields so parents appear before dependents."""
        ...

    def get_dependent_fields(self, field_id: str, fields: list[UserField]) -> list[UserField]:
        """Return fields that depend on the given field_id."""
        ...

"""HierarchyEngine — pure logic for cascading field dependencies.

No I/O. Resolves option filtering and dependency ordering.
"""

from __future__ import annotations

from prism.models.package_info import UserField


class HierarchyEngine:
    """Pure-logic hierarchy engine — no I/O."""

    def filter_options(self, field: UserField, parent_value: str) -> list[str]:
        """Return filtered options for a dependent field given parent value.

        If field has an option_map and parent_value is a key, return those options.
        Otherwise return the full options list (no filtering).
        """
        if not field.option_map or not parent_value:
            return field.options

        return field.option_map.get(parent_value, field.options)

    def resolve_dependency_order(self, fields: list[UserField]) -> list[UserField]:
        """Sort fields so parents appear before dependents.

        Uses topological sort. Fields without depends_on come first.
        """
        field_by_id = {f.id: f for f in fields}
        visited: set[str] = set()
        result: list[UserField] = []

        def visit(fid: str) -> None:
            if fid in visited:
                return
            visited.add(fid)
            f = field_by_id.get(fid)
            if f is None:
                return
            if f.depends_on and f.depends_on in field_by_id:
                visit(f.depends_on)
            result.append(f)

        for f in fields:
            visit(f.id)

        return result

    def get_dependent_fields(self, field_id: str, fields: list[UserField]) -> list[UserField]:
        """Return fields that directly depend on field_id."""
        return [f for f in fields if f.depends_on == field_id]

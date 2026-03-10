"""Package source resolution — private submodule.

Resolves where a package comes from (local filesystem, npm registry, or URL).
No accessor dependencies — pure logic.
"""

from __future__ import annotations

_DEFAULT_UNPKG_URL = "https://unpkg.com"
_DEFAULT_NPM_REGISTRY = "https://registry.npmjs.org"
_PRISM_SCOPE = "@prism"
_LOCAL_SUFFIXES = ["", "-config"]
_LOCAL_TRANSFORMS = [
    lambda s: s,
    lambda s: s.replace("-", "_"),
]


def resolve_package_source(package_name: str, sources: list[dict] | None = None) -> dict:
    """Resolve where a package comes from (local, npm, or url)."""
    if sources:
        for source in sources:
            source_type = source.get("type", "")
            if source_type == "local":
                return resolve_local(package_name, source)
            elif source_type == "npm":
                return resolve_npm(package_name, source)
            elif source_type == "url":
                return {"type": "url", "package_name": package_name, "url": source.get("url", "")}

    if package_name.startswith("@") or package_name.startswith(_PRISM_SCOPE):
        return resolve_npm(package_name, {})

    return resolve_local(package_name, {})


def resolve_local(package_name: str, source: dict) -> dict:
    """Resolve a local package source."""
    stripped = package_name.replace(f"{_PRISM_SCOPE}/", "").replace("-config", "")
    local_names: list[str] = []
    for transform in _LOCAL_TRANSFORMS:
        base = transform(stripped)
        for suffix in _LOCAL_SUFFIXES:
            candidate = base + suffix
            if candidate not in local_names:
                local_names.append(candidate)
    return {
        "type": "local",
        "package_name": package_name,
        "local_names": local_names,
        "base_path": source.get("path", ""),
    }


def resolve_npm(package_name: str, source: dict) -> dict:
    """Resolve an npm package source."""
    npm_name = package_name if package_name.startswith("@") else f"{_PRISM_SCOPE}/{package_name}"
    registry_url = source.get("registry", _DEFAULT_NPM_REGISTRY)
    unpkg_url = source.get("unpkg_url", _DEFAULT_UNPKG_URL)
    return {"type": "npm", "package_name": npm_name, "registry_url": registry_url, "npm_url": f"{unpkg_url}/{npm_name}"}

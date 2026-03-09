"""ResolutionEngine — resolve package source (local, npm, url).

Extracted from scripts/npm_package_fetcher.py. Pure computation —
determines where a package comes from, does not fetch it.

Volatility: medium — changes as new source types are supported.
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


class ResolutionEngine:
    """Resolve whether a prism comes from local or remote."""

    def resolve(self, package_name: str, sources: list[dict] | None = None) -> dict:
        """Resolve a package source.

        Returns a source descriptor dict with type, url/path, and metadata.
        """
        if sources:
            for source in sources:
                source_type = source.get("type", "")
                if source_type == "local":
                    return self._resolve_local(package_name, source)
                elif source_type == "npm":
                    return self._resolve_npm(package_name, source)
                elif source_type == "url":
                    return {
                        "type": "url",
                        "package_name": package_name,
                        "url": source.get("url", ""),
                    }

        if package_name.startswith("@") or package_name.startswith(_PRISM_SCOPE):
            return self._resolve_npm(package_name, {})

        return self._resolve_local(package_name, {})

    def _resolve_local(self, package_name: str, source: dict) -> dict:
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

    def _resolve_npm(self, package_name: str, source: dict) -> dict:
        if not package_name.startswith("@"):
            npm_name = f"{_PRISM_SCOPE}/{package_name}"
        else:
            npm_name = package_name

        registry_url = source.get("registry", _DEFAULT_NPM_REGISTRY)
        unpkg_url = source.get("unpkg_url", _DEFAULT_UNPKG_URL)

        return {
            "type": "npm",
            "package_name": npm_name,
            "registry_url": registry_url,
            "npm_url": f"{unpkg_url}/{npm_name}",
        }

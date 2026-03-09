"""Package discovery & metadata API flow.

Routes for listing packages, getting metadata, tiers, user fields,
and prism config. Delegates to PackageManager via DI container.

Volatility: medium — route shape stable; response format may evolve.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

packages_bp = Blueprint("packages", __name__)


def _pm():
    """Get PackageManager from DI container."""
    return current_app.config["container"].package_manager


@packages_bp.route("/api/packages")
def list_packages():
    """List all discoverable prism packages with validation status."""
    try:
        pm = _pm()
        packages = pm.list_packages()
        results = pm.validate_all()

        valid_packages = []
        invalid_packages = []

        for pkg in packages:
            is_valid, errors, warnings = results.get(pkg.name, (True, [], []))
            entry = {
                "id": pkg.dir_name or pkg.name,
                "name": pkg.name,
                "displayName": pkg.display_name or pkg.name.replace("-", " ").title(),
                "description": pkg.description,
                "version": pkg.version,
                "source": "local",
                "path": pkg.path,
            }
            if is_valid:
                entry["warnings"] = warnings
                entry["default"] = pkg.default
                valid_packages.append(entry)
            else:
                entry["errors"] = errors
                invalid_packages.append(entry)

        return jsonify(
            {
                "packages": valid_packages,
                "invalid_packages": invalid_packages,
                "stats": {
                    "valid": len(valid_packages),
                    "invalid": len(invalid_packages),
                    "total": len(valid_packages) + len(invalid_packages),
                },
            }
        )
    except Exception as e:
        return jsonify({"packages": [], "invalid_packages": [], "error": str(e)})


@packages_bp.route("/api/package/<package_name>/metadata")
def get_metadata(package_name):
    """Get package metadata — what features/sections are available."""
    try:
        pm = _pm()
        info = pm.get_info(package_name)
        tiers = pm.get_tiers(package_name)

        # Detect optional tiers (tiers with at least one non-required item)
        has_optional_tiers = any(any(not t.required for t in tier_items) for tier_items in tiers.values())

        # Check for tools — base config or any bundled profile may have them.
        # When bundled_prisms exist, profiles may add tools after merge, so assume true.
        container = current_app.config["container"]
        config = container.file_accessor.get_package_config(container._prisms_dir, package_name)
        pkg_section = config.get("package", {})
        has_tools = (
            "tools_required" in config
            or "tools_selected" in config
            or "tools" in pkg_section
            or "tools" in config
            or bool(config.get("bundled_prisms"))
        )

        user_fields = pm.get_user_fields(package_name)

        return jsonify(
            {
                "name": package_name,
                "display_name": info.display_name,
                "description": info.description,
                "has_tiers": info.has_tiers,
                "has_optional_tiers": has_optional_tiers,
                "has_sub_orgs": False,
                "has_departments": False,
                "has_teams": False,
                "has_tools": has_tools,
                "user_fields_count": len(user_fields),
                "package_type": info.package_type,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)})


@packages_bp.route("/api/package/<package_name>/tiers")
def get_tiers(package_name):
    """Get optional bundled_prisms tier structure."""
    try:
        pm = _pm()
        tiers = pm.get_tiers(package_name)

        optional_tiers = []
        for tier_name, tier_items in tiers.items():
            optional_items = [t for t in tier_items if not t.required]
            if not optional_items:
                continue
            optional_tiers.append(
                {
                    "name": tier_name,
                    "label": tier_name.replace("_", " ").title(),
                    "required": False,
                    "options": [{"id": t.id, "name": t.name, "description": t.description} for t in optional_items],
                }
            )

        return jsonify({"optional_tiers": optional_tiers})
    except Exception as e:
        return jsonify({"error": str(e), "optional_tiers": []})


@packages_bp.route("/api/package/<package_name>/user-fields")
def get_user_fields(package_name):
    """Get user info fields for a package."""
    try:
        pm = _pm()
        fields = pm.get_user_fields(package_name)

        if not fields:
            # Default fields when none defined
            return jsonify(
                {
                    "fields": [
                        {
                            "id": "name",
                            "label": "Full Name",
                            "type": "text",
                            "required": True,
                            "placeholder": "John Doe",
                        },
                        {
                            "id": "email",
                            "label": "Email",
                            "type": "email",
                            "required": True,
                            "placeholder": "john.doe@example.com",
                        },
                    ]
                }
            )

        return jsonify(
            {
                "fields": [
                    {
                        "id": f.id,
                        "label": f.label,
                        "type": f.type,
                        "required": f.required,
                        "placeholder": f.placeholder,
                        "options": f.options if f.options else None,
                    }
                    for f in fields
                ]
            }
        )
    except Exception as e:
        return jsonify({"fields": [], "error": str(e)})


@packages_bp.route("/api/package/<package_name>/config")
def get_config(package_name):
    """Get prism_config section for meta-prism configuration."""
    try:
        container = current_app.config["container"]
        im = container.installation_manager
        prism_config = im.load_prism_config(package_name)

        # Convert to dict for JSON serialization
        config_dict = {
            "theme": prism_config.theme,
            "sources": prism_config.sources,
            "npm_registry": prism_config.npm_registry,
            "unpkg_url": prism_config.unpkg_url,
            "proxies": prism_config.proxies,
            "branding": {
                "name": prism_config.branding.name,
                "tagline": prism_config.branding.tagline,
                "logo_text": prism_config.branding.logo_text,
                "logo_icon": prism_config.branding.logo_icon,
                "page_title": prism_config.branding.page_title,
                "header_title": prism_config.branding.header_title,
                "header_subtitle": prism_config.branding.header_subtitle,
                "favicon_emoji": prism_config.branding.favicon_emoji,
            },
        }

        return jsonify({"prism_config": config_dict, "package_name": package_name})
    except Exception as e:
        return jsonify({"prism_config": None, "error": str(e)})


@packages_bp.route("/api/package/<package_name>/tools")
def get_tools(package_name):
    """Get tools from the package, optionally merged with selected sub-prisms."""
    from flask import request

    try:
        container = current_app.config["container"]
        im = container.installation_manager

        # Get selected sub-prisms from query params (e.g. ?environment=personal)
        selected_sub_prisms = {}
        config = container.file_accessor.get_package_config(container._prisms_dir, package_name)
        bundled = config.get("bundled_prisms", {})
        for tier_name in bundled:
            val = request.args.get(tier_name)
            if val:
                selected_sub_prisms[tier_name] = val

        # Merge tiers to get the effective config
        merged = im.merge_tiers(config, selected_sub_prisms)

        # Collect tools from merged config
        tools_required = merged.get("tools_required", config.get("tools_required", []))
        tools_optional = merged.get("tools_optional", config.get("tools_optional", []))

        seen = {}
        for tool in tools_required:
            if isinstance(tool, dict):
                tid = tool.get("name", "")
                seen[tid] = {
                    "id": tid,
                    "name": tid.replace("-", " ").title(),
                    "description": tool.get("description", ""),
                    "required": True,
                }

        for tool in tools_optional:
            if isinstance(tool, dict):
                tid = tool.get("name", "")
                if tid not in seen:
                    seen[tid] = {
                        "id": tid,
                        "name": tid.replace("-", " ").title(),
                        "description": tool.get("description", ""),
                        "required": False,
                    }

        tools = list(seen.values())
        return jsonify({"tools": tools, "has_tools": len(tools) > 0})
    except Exception as e:
        return jsonify({"tools": [], "has_tools": False, "error": str(e)})

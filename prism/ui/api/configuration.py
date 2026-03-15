"""Configuration & settings API flow.

Handles legacy organization/tools routes and static asset serving.

Volatility: low — these routes are stable or legacy.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from flask import Blueprint, current_app, jsonify, send_from_directory

configuration_bp = Blueprint("configuration", __name__)


def _root_dir() -> Path:
    """Get the project root directory."""
    return current_app.config["prisms_dir"].parent


@configuration_bp.route("/api/organizations")
def get_organizations():
    """Get available organizations from config (legacy)."""
    config_dir = _root_dir() / "config"
    inheritance_path = config_dir / "inheritance.yaml"

    if not inheritance_path.exists():
        return jsonify({"sub_orgs": [], "departments": [], "teams": []})

    with open(inheritance_path) as f:
        config = yaml.safe_load(f) or {}

    return jsonify(
        {
            "sub_orgs": config.get("available_sub_orgs", []),
            "departments": config.get("available_departments", []),
            "teams": config.get("available_teams", []),
        }
    )


@configuration_bp.route("/api/tools")
def get_tools():
    """Get available tools from tools.yaml."""
    config_dir = _root_dir() / "config"
    tools_path = config_dir / "tools.yaml"

    if not tools_path.exists():
        return jsonify({"tools": []})

    with open(tools_path) as f:
        config = yaml.safe_load(f) or {}

    tools = []
    for tool_id, tool_config in config.get("tools", {}).items():
        tools.append(
            {
                "id": tool_id,
                "name": tool_id.replace("-", " ").title(),
                "description": tool_config.get("description", ""),
                "required": tool_config.get("required", False),
            }
        )

    return jsonify({"tools": tools})


@configuration_bp.route("/api/history")
def get_history():
    """Scan for previous prism installations."""
    from prism.cli.history import _find_installs

    home = Path.home()
    search = [home, home / "dev", home / "projects", home / "workspace", home / "Development"]
    installs = _find_installs(search)
    return jsonify({"installs": installs})


@configuration_bp.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve static assets (branding, etc.)."""
    assets_dir = _root_dir() / "assets"
    if not (assets_dir / filename).exists():
        # Fall back to bundled assets when running from pip install
        bundled_dir = Path(__file__).parent.parent / "static" / "assets"
        return send_from_directory(str(bundled_dir), filename)
    return send_from_directory(str(assets_dir), filename)

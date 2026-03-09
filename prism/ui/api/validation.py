"""Validation API flow.

Handles package config validation routes. Delegates to PackageManager.

Volatility: low — validation endpoint is stable.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

validation_bp = Blueprint("validation", __name__)


@validation_bp.route("/api/package/<package_name>/validate-configs")
def validate_configs(package_name):
    """Validate a package's configuration."""
    try:
        pm = current_app.config["container"].package_manager
        is_valid, errors, warnings = pm.validate(package_name)

        return jsonify(
            {
                "valid": is_valid,
                "summary": {
                    "total_files": 1,
                    "invalid_files": 0 if is_valid else 1,
                    "total_errors": len(errors),
                    "total_warnings": len(warnings),
                },
                "results": [
                    {
                        "file": "package.yaml",
                        "valid": is_valid,
                        "errors": errors,
                        "warnings": warnings,
                    }
                ],
            }
        )
    except FileNotFoundError:
        return jsonify({"valid": False, "error": f"Package not found: {package_name}"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

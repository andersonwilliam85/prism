"""Installation execution API flow.

Handles the POST /api/install route — delegates to InstallationManager.

Volatility: low — install endpoint shape is stable.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

installation_bp = Blueprint("installation", __name__)


@installation_bp.route("/api/install", methods=["POST"])
def install():
    """Run the full installation pipeline via InstallationManager."""
    data = request.json or {}

    prism_id = (data.get("package") or "").strip()
    if not prism_id:
        return jsonify({"success": False, "error": "No prism specified"}), 400

    user_info = data.get("userInfo", {})
    selected_sub_prisms = data.get("selectedSubPrisms", {})
    tools_selected = data.get("toolsSelected", [])
    tools_excluded = data.get("toolsExcluded", [])

    try:
        container = current_app.config["container"]
        im = container.installation_manager

        # Collect progress messages
        progress_log = []

        def progress_callback(step, message, level):
            progress_log.append({"step": step, "message": message, "level": level})

        im.set_progress_callback(progress_callback)

        result = im.install(
            package_name=prism_id,
            user_info=user_info,
            selected_sub_prisms=selected_sub_prisms,
            tools_selected=tools_selected,
            tools_excluded=tools_excluded,
        )

        if result.success:
            return jsonify(
                {
                    "success": True,
                    "message": "Installation completed successfully!",
                    "workspace": "",
                    "progress": progress_log,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.error or "Installation failed",
                        "progress": progress_log,
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

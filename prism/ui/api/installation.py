"""Installation execution API flow.

Handles install, sudo validation, and session management routes.
Delegates to InstallationManager and SudoValidationEngine/SudoAccessor.

Volatility: low — install endpoint shape is stable.
"""

from __future__ import annotations

import json
import queue
import threading
import uuid
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request

from prism.models.installation import SudoSession

installation_bp = Blueprint("installation", __name__)

# In-memory session store — keyed by token. Never persisted.
_sudo_sessions: dict[str, SudoSession] = {}

# Active installations — keyed by install_id.
_active_installs: dict[str, dict] = {}


@installation_bp.route("/api/install", methods=["POST"])
def install():
    """Run the full installation pipeline via InstallationManager."""
    data = request.json or {}

    prism_id = (data.get("package") or "").strip()
    if not prism_id:
        return jsonify({"success": False, "error": "No prism specified"}), 400

    user_info = data.get("userInfo", {})
    target_dir = data.get("targetDir", "")
    if target_dir:
        user_info["workspace_dir"] = target_dir
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
            workspace = user_info.get("workspace_dir", str(Path.home() / "workspace"))
            return jsonify(
                {
                    "success": True,
                    "message": "Installation completed successfully!",
                    "workspace": workspace,
                    "progress": progress_log,
                }
            )
        else:
            resp = {
                "success": False,
                "error": result.error or "Installation failed",
                "progress": progress_log,
            }
            if result.rollback_results:
                resp["rollback"] = result.rollback_results
            return jsonify(resp), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@installation_bp.route("/api/install/stream", methods=["POST"])
def install_stream():
    """Run installation with Server-Sent Events for real-time progress.

    Returns an SSE stream. Each event is a JSON object:
      data: {"type": "progress", "step": "...", "message": "...", "level": "..."}
      data: {"type": "complete", "success": true, "workspace": "..."}
      data: {"type": "error", "error": "..."}
      data: {"type": "cancelled", "rollback": [...]}
    """
    data = request.json or {}

    prism_id = (data.get("package") or "").strip()
    if not prism_id:
        return jsonify({"success": False, "error": "No prism specified"}), 400

    user_info = data.get("userInfo", {})
    target_dir = data.get("targetDir", "")
    if target_dir:
        user_info["workspace_dir"] = target_dir
    selected_sub_prisms = data.get("selectedSubPrisms", {})
    tools_selected = data.get("toolsSelected", [])
    tools_excluded = data.get("toolsExcluded", [])

    install_id = str(uuid.uuid4())[:8]
    msg_queue: queue.Queue = queue.Queue()
    cancel_event = threading.Event()

    _active_installs[install_id] = {"cancel_event": cancel_event, "queue": msg_queue}

    # Send install_id as first event so client can cancel
    msg_queue.put(json.dumps({"type": "started", "install_id": install_id}))

    container = current_app.config["container"]
    im = container.installation_manager

    def progress_callback(step, message, level):
        msg_queue.put(json.dumps({"type": "progress", "step": step, "message": message, "level": level}))

    def run_install():
        try:
            im.set_progress_callback(progress_callback)
            im.set_cancel_event(cancel_event)

            result = im.install(
                package_name=prism_id,
                user_info=user_info,
                selected_sub_prisms=selected_sub_prisms,
                tools_selected=tools_selected,
                tools_excluded=tools_excluded,
            )

            if result.success:
                workspace = user_info.get("workspace_dir", str(Path.home() / "workspace"))
                msg_queue.put(json.dumps({"type": "complete", "success": True, "workspace": workspace}))
            elif result.rollback_results:
                msg_queue.put(
                    json.dumps(
                        {
                            "type": "cancelled" if "cancelled" in (result.error or "").lower() else "error",
                            "error": result.error,
                            "rollback": result.rollback_results,
                        }
                    )
                )
            else:
                msg_queue.put(json.dumps({"type": "error", "error": result.error or "Installation failed"}))
        except Exception as e:
            msg_queue.put(json.dumps({"type": "error", "error": str(e)}))
        finally:
            msg_queue.put(None)  # Sentinel to close stream
            im.set_cancel_event(None)
            _active_installs.pop(install_id, None)

    thread = threading.Thread(target=run_install, daemon=True)
    thread.start()

    def generate():
        while True:
            msg = msg_queue.get()
            if msg is None:
                break
            yield f"data: {msg}\n\n"

    return Response(
        generate(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@installation_bp.route("/api/install/cancel", methods=["POST"])
def cancel_install():
    """Cancel an in-progress installation.

    Expects JSON: {"install_id": "..."}
    Signals the installation thread to stop, which triggers auto-rollback.
    """
    data = request.json or {}
    install_id = data.get("install_id", "")

    entry = _active_installs.get(install_id)
    if not entry:
        return jsonify({"success": False, "error": "No active installation found"}), 404

    entry["cancel_event"].set()
    return jsonify({"success": True, "message": "Cancellation requested"})


# ------------------------------------------------------------------
# Sudo session endpoints
# ------------------------------------------------------------------


@installation_bp.route("/api/installation/validate-sudo", methods=["POST"])
def validate_sudo():
    """Validate a sudo password and create/update a session.

    Expects JSON: {"password": "...", "token": "..."}
    If token is provided, reuses existing session (for retries).
    If not, creates a new session.
    """
    data = request.json or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"success": False, "error": "Password required"}), 400

    container = current_app.config["container"]
    engine = container.sudo_validation_engine
    accessor = container.sudo_accessor

    # Check sudo availability
    if not accessor.is_sudo_available():
        return jsonify({"success": False, "error": "sudo not available on this system"}), 400

    # Get or create session
    token = data.get("token")
    session = _sudo_sessions.get(token) if token else None
    if session is None:
        session = engine.create_session()
        _sudo_sessions[session.token] = session

    # Check lockout
    if not engine.validate_session(session):
        if session.is_locked:
            return jsonify({"success": False, "error": "Too many attempts. Try again later.", "locked": True}), 429
        if session.is_expired:
            _sudo_sessions.pop(session.token, None)
            return jsonify({"success": False, "error": "Session expired", "expired": True}), 401

    # Validate password via accessor
    valid = accessor.validate_password(password)
    session = engine.record_attempt(session, valid)
    _sudo_sessions[session.token] = session

    if valid:
        return jsonify({"success": True, "token": session.token})

    remaining = session.max_attempts - session.attempts
    resp = {"success": False, "error": "Invalid password", "token": session.token}
    if remaining > 0:
        resp["remaining_attempts"] = remaining
    else:
        resp["locked"] = True
        resp["error"] = "Too many attempts. Try again in 30 seconds."
    status = 429 if session.is_locked else 401
    return jsonify(resp), status


@installation_bp.route("/api/installation/sudo-session/<token>", methods=["GET"])
def sudo_session_status(token: str):
    """Check if a sudo session is still valid."""
    session = _sudo_sessions.get(token)
    if session is None:
        return jsonify({"valid": False, "error": "Session not found"}), 404

    container = current_app.config["container"]
    engine = container.sudo_validation_engine
    valid = engine.validate_session(session)

    if not valid and session.is_expired:
        _sudo_sessions.pop(token, None)

    return jsonify({"valid": valid, "expired": session.is_expired, "locked": session.is_locked})

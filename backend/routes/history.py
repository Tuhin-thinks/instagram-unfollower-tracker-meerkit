from flask import Blueprint, jsonify

from backend.services import persistence

bp = Blueprint("history", __name__, url_prefix="/api")


@bp.get("/history")
def history():
    return jsonify(persistence.get_scan_index())


@bp.get("/diff/latest")
def latest_diff():
    diff = persistence.get_latest_diff()
    return jsonify(diff)


@bp.get("/diff/<diff_id>")
def get_diff(diff_id: str):
    # Only allow alphanumeric + underscore diff IDs to prevent path traversal
    if not all(c.isalnum() or c == "_" for c in diff_id):
        return jsonify({"error": "Invalid diff ID"}), 400
    diff = persistence.get_diff(diff_id)
    if not diff:
        return jsonify({"error": "Diff not found"}), 404
    return jsonify(diff)

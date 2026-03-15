from flask import Blueprint, jsonify, request, session

from backend.config import profile_data_dir
from backend.services import auth, persistence

bp = Blueprint("history", __name__, url_prefix="/api")


def _data_dir_or_error() -> tuple[None, tuple[dict, int]] | tuple[object, None]:
    """Resolve scoped data directory from logged-in user and selected instagram user."""
    app_user_id = session.get("app_user_id")
    if not app_user_id:
        return None, ({"error": "Not logged in"}, 401)

    instagram_user_id = request.args.get("profile_id") or request.args.get(
        "instagram_user_id"
    )
    if not instagram_user_id:
        instagram_user_id = auth.get_active_instagram_user_id(app_user_id)
    if not instagram_user_id:
        return None, ({"error": "No active instagram user selected"}, 400)

    instagram_user = auth.get_instagram_user(app_user_id, instagram_user_id)
    if not instagram_user:
        return None, ({"error": "Instagram user not found"}, 404)

    return profile_data_dir(app_user_id, instagram_user_id), None


@bp.get("/history")
def history():
    data_dir, err = _data_dir_or_error()
    if err:
        body, code = err
        return jsonify(body), code
    return jsonify(persistence.get_scan_index(data_dir))


@bp.get("/diff/latest")
def latest_diff():
    data_dir, err = _data_dir_or_error()
    if err:
        body, code = err
        return jsonify(body), code
    diff = persistence.get_latest_diff(data_dir)
    return jsonify(diff)


@bp.get("/diff/<diff_id>")
def get_diff(diff_id: str):
    # Only allow alphanumeric + underscore diff IDs to prevent path traversal
    if not all(c.isalnum() or c == "_" for c in diff_id):
        return jsonify({"error": "Invalid diff ID"}), 400
    data_dir, err = _data_dir_or_error()
    if err:
        body, code = err
        return jsonify(body), code
    diff = persistence.get_diff(data_dir, diff_id)
    if not diff:
        return jsonify({"error": "Diff not found"}), 404
    return jsonify(diff)

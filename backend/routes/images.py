from flask import Blueprint, jsonify, send_file

from backend.services import image_cache, persistence

bp = Blueprint("images", __name__, url_prefix="/api")


@bp.get("/image/<pk_id>")
def get_image(pk_id: str):
    # Validate pk_id is numeric to prevent path traversal and SSRF via crafted IDs
    if not pk_id.isdigit():
        return jsonify({"error": "Invalid pk_id"}), 400

    # Serve from disk cache if available
    cached = image_cache.get_cached_image_path(pk_id)
    if cached:
        resp = send_file(cached, mimetype="image/jpeg")
        resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
        return resp

    # Look up the original URL from our own stored scan data (not from client input)
    url = persistence.get_profile_pic_url(pk_id)
    if not url:
        return jsonify({"error": "User not found in latest scan"}), 404

    cached = image_cache.fetch_and_cache(pk_id, url)
    if not cached:
        return jsonify({"error": "Could not fetch image"}), 502

    resp = send_file(cached, mimetype="image/jpeg")
    resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
    return resp

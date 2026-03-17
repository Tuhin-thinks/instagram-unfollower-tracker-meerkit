from flask import Blueprint, jsonify, request, send_file, session

from backend.config import IMAGE_CACHE_DIR, profile_data_dir
from backend.services import auth, image_cache, persistence
from backend.services.downloader import enqueue_image_download

bp = Blueprint("images", __name__, url_prefix="/api")


@bp.get("/image/<pk_id>")
def get_image(pk_id: str):
    # Validate pk_id is numeric to prevent path traversal and SSRF via crafted IDs
    if not pk_id.isdigit():
        return jsonify({"error": "Invalid pk_id"}), 400

    app_user_id = session.get("app_user_id")
    if not app_user_id:
        return jsonify({"error": "Not logged in"}), 401

    instagram_user_id = request.args.get("profile_id") or request.args.get(
        "instagram_user_id"
    )
    if not instagram_user_id:
        instagram_user_id = auth.get_active_instagram_user_id(app_user_id)
    if not instagram_user_id:
        return jsonify({"error": "No active instagram user selected"}), 400

    instagram_user = auth.get_instagram_user(app_user_id, instagram_user_id)
    if not instagram_user:
        return jsonify({"error": "Instagram user not found"}), 404

    # data_dir = profile_data_dir(app_user_id, instagram_user_id)
    # cache_dir = data_dir / "image_cache"

    # Serve from disk cache if available
    cached = image_cache.get_cached_image_path(pk_id)
    if cached:
        resp = send_file(cached, mimetype="image/jpeg")
        resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
        return resp

    else:
        enqueue_image_download(app_user_id, pk_id, instagram_user["profile_pic_url"])
        resp = send_file(
            IMAGE_CACHE_DIR / "no-img-available.jpeg", mimetype="image/jpeg"
        )
        resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
        return resp

    # # Look up the original URL from our own stored scan data (not from client input)
    # url = persistence.get_profile_pic_url(data_dir, pk_id)
    # if not url:
    #     return jsonify({"error": "User not found in latest scan"}), 404

    # cached = image_cache.fetch_and_cache(pk_id, url, cache_dir)
    # if not cached:
    #     return jsonify({"error": "Could not fetch image"}), 502

    # resp = send_file(cached, mimetype="image/jpeg")
    # resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
    # return resp

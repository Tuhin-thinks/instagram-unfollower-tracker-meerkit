from flask import Blueprint, jsonify

from backend.services import persistence, scan_runner

bp = Blueprint("scan", __name__, url_prefix="/api")


@bp.post("/scan")
def trigger_scan():
    started = scan_runner.start_scan()
    if not started:
        return jsonify({"error": "Scan already in progress"}), 409
    return jsonify({"message": "scan started"}), 202


@bp.get("/scan/status")
def scan_status():
    return jsonify(scan_runner.get_status())


@bp.get("/summary")
def summary():
    meta = persistence.get_latest_scan_meta()
    if not meta:
        return jsonify(None)
    # Enrich with diff counts so the UI has a single call for header stats
    if meta.get("diff_id"):
        diff = persistence.get_diff(meta["diff_id"])
        if diff:
            meta = {
                **meta,
                "new_count": diff["new_count"],
                "unfollow_count": diff["unfollow_count"],
            }
    return jsonify(meta)

import json
from pathlib import Path

from backend.config import DIFFS_DIR, SCAN_INDEX_FILE, SCANS_DIR


def get_scan_index() -> list[dict]:
    """Return all scan metadata entries, newest first."""
    if not SCAN_INDEX_FILE.exists():
        return []
    entries: list[dict] = []
    with open(SCAN_INDEX_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return list(reversed(entries))


def get_latest_scan_meta() -> dict | None:
    """Return the newest scan metadata entry, if present."""
    index = get_scan_index()
    return index[0] if index else None


def get_diff(diff_id: str) -> dict | None:
    """Return a persisted diff payload by diff ID."""
    path = DIFFS_DIR / f"{diff_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_latest_diff() -> dict | None:
    """Return the latest diff payload for the newest scan."""
    meta = get_latest_scan_meta()
    if not meta or not meta.get("diff_id"):
        return None
    return get_diff(meta["diff_id"])


def get_profile_pic_url(pk_id: str) -> str | None:
    """Find the profile_pic_url for a pk_id by scanning the latest snapshot."""
    snapshots = sorted(SCANS_DIR.glob("scan_*.jsonl"))
    if not snapshots:
        return None
    with open(snapshots[-1]) as f:
        for line in f.readlines()[1:]:  # skip timestamp header
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    if data.get("pk_id") == pk_id:
                        return data.get("profile_pic_url")
                except json.JSONDecodeError:
                    continue
    return None

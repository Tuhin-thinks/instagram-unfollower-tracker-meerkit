import json
from pathlib import Path


def _scan_index_file(data_dir: Path) -> Path:
    """Return the scan index file path under a scoped data directory."""
    return data_dir / "scan_index.jsonl"


def _diffs_dir(data_dir: Path) -> Path:
    """Return the scoped diffs directory."""
    return data_dir / "diffs"


def _scans_dir(data_dir: Path) -> Path:
    """Return the scoped scans directory."""
    return data_dir / "scans"


def get_scan_index(data_dir: Path) -> list[dict]:
    """Return all scan metadata entries, newest first."""
    index_file = _scan_index_file(data_dir)
    if not index_file.exists():
        return []
    entries: list[dict] = []
    with open(index_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return list(reversed(entries))


def get_latest_scan_meta(data_dir: Path) -> dict | None:
    """Return the newest scan metadata entry, if present."""
    index = get_scan_index(data_dir)
    return index[0] if index else None


def get_diff(data_dir: Path, diff_id: str) -> dict | None:
    """Return a persisted diff payload by diff ID."""
    path = _diffs_dir(data_dir) / f"{diff_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_latest_diff(data_dir: Path) -> dict | None:
    """Return the latest diff payload for the newest scan."""
    meta = get_latest_scan_meta(data_dir)
    if not meta or not meta.get("diff_id"):
        return None
    return get_diff(data_dir, meta["diff_id"])


def get_profile_pic_url(data_dir: Path, pk_id: str) -> str | None:
    """Find the profile_pic_url for a pk_id by scanning the latest snapshot."""
    snapshots = sorted(_scans_dir(data_dir).glob("scan_*.jsonl"))
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

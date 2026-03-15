from pathlib import Path

import requests as _requests

from backend.config import IMAGE_CACHE_DIR

# Small in-process memory layer: pk_id → resolved local path string
_memory_cache: dict[str, str] = {}


def get_cached_image_path(pk_id: str) -> Path | None:
    """Return the cached image Path if it exists on disk, else None."""
    if pk_id in _memory_cache:
        p = Path(_memory_cache[pk_id])
        return p if p.exists() else None
    path = IMAGE_CACHE_DIR / f"{pk_id}.jpg"
    if path.exists():
        _memory_cache[pk_id] = str(path)
        return path
    return None


def fetch_and_cache(pk_id: str, url: str) -> Path | None:
    """Download and cache a trusted profile image URL under the follower pk_id."""
    path = IMAGE_CACHE_DIR / f"{pk_id}.jpg"
    if path.exists():
        _memory_cache[pk_id] = str(path)
        return path
    try:
        resp = _requests.get(url, timeout=10, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return None
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        _memory_cache[pk_id] = str(path)
        return path
    except Exception:
        return None

from pathlib import Path

import requests as _requests

from backend.config import IMAGE_CACHE_DIR

# Small in-process memory layer: pk_id → resolved local path string
_memory_cache: dict[str, str] = {}


def get_cached_image_path(pk_id: str, cache_dir: Path = IMAGE_CACHE_DIR) -> Path | None:
    """Return the cached image Path if it exists on disk, else None."""
    cache_key = f"{cache_dir}:{pk_id}"
    if cache_key in _memory_cache:
        p = Path(_memory_cache[cache_key])
        return p if p.exists() else None
    path = cache_dir / f"{pk_id}.jpg"
    if path.exists():
        _memory_cache[cache_key] = str(path)
        return path
    return None


def fetch_and_cache(
    pk_id: str, url: str, cache_dir: Path = IMAGE_CACHE_DIR
) -> Path | None:
    """Download and cache a trusted profile image URL under the follower pk_id."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key = f"{cache_dir}:{pk_id}"
    path = cache_dir / f"{pk_id}.jpg"
    if path.exists():
        _memory_cache[cache_key] = str(path)
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
        _memory_cache[cache_key] = str(path)
        return path
    except Exception:
        return None

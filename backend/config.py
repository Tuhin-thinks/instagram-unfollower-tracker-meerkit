from pathlib import Path

# Workspace root is the parent of this backend/ package
WORKSPACE_ROOT = Path(__file__).parent.parent

DATA_DIR = WORKSPACE_ROOT / "data"
SCANS_DIR = DATA_DIR / "scans"
DIFFS_DIR = DATA_DIR / "diffs"
IMAGE_CACHE_DIR = DATA_DIR / "image_cache"
SCAN_INDEX_FILE = DATA_DIR / "scan_index.jsonl"

# Create directories on import so nothing needs to worry about them not existing
for _d in [SCANS_DIR, DIFFS_DIR, IMAGE_CACHE_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

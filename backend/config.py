from pathlib import Path

# Workspace root is the parent of this backend/ package
WORKSPACE_ROOT = Path(__file__).parent.parent

DATA_DIR = WORKSPACE_ROOT / "data"
USERS_DIR = DATA_DIR / "users"
SCANS_DIR = DATA_DIR / "scans"
DIFFS_DIR = DATA_DIR / "diffs"
IMAGE_CACHE_DIR = DATA_DIR / "image_cache"
SCAN_INDEX_FILE = DATA_DIR / "scan_index.jsonl"

# Create directories on import so nothing needs to worry about them not existing
for _d in [DATA_DIR, USERS_DIR, SCANS_DIR, DIFFS_DIR, IMAGE_CACHE_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


def user_dir(app_user_id: str) -> Path:
    """Return the root directory for one app user's persisted data."""
    return USERS_DIR / app_user_id


def profile_dir(app_user_id: str, profile_id: str) -> Path:
    """Return the directory for one user's trackable target profile."""
    return user_dir(app_user_id) / "profiles" / profile_id


def profile_data_dir(app_user_id: str, profile_id: str) -> Path:
    """Return the data directory that holds scans, diffs, and cache for a profile."""
    return profile_dir(app_user_id, profile_id) / "data"

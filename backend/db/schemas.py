ACCOUNTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    profile_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    create_date TEXT NOT NULL,
    is_private INTEGER NOT NULL,
    is_follower INTEGER NOT NULL,
    is_following INTEGER NOT NULL,
    reference_profile_id TEXT NOT NULL
);"""

IMAGE_CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS image_cache (
    profile_id TEXT NOT NULL,
    image_id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    local_path TEXT NOT NULL,
    create_date TEXT NOT NULL
    );"""

PROFILE_AUDIENCE_EVENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS profile_audience_events (
    profile_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    date TEXT NOT NULL,
    event_data TEXT
);"""


schema_collection = {
    "accounts": ACCOUNTS_SCHEMA,
    "image_cache": IMAGE_CACHE_SCHEMA,
    "profile_audience_events": PROFILE_AUDIENCE_EVENTS_SCHEMA,
}

import threading
from pathlib import Path

from flask import g, session

import insta_interface as ii
from backend.config import app_user_db
from backend.db.db_handler import SqliteDBHandler

_thread_local = threading.local()


def get_worker_db(db_path: Path | None = None) -> SqliteDBHandler:
    if not hasattr(_thread_local, "db"):
        if not db_path:
            raise ValueError("db_path is required for worker threads")
        _thread_local.db = SqliteDBHandler(db_path=db_path)
    return _thread_local.db


def init_worker_db(app_user_id: str) -> SqliteDBHandler:
    """Initialize the worker thread's database handler for the given app user id."""
    db_path = app_user_db(app_user_id)
    return get_worker_db(db_path=db_path)


def retrieve_img_path_by_pk_id(pk_id: str) -> str | None:
    """Convenience method to retrieve cached image path by pk_id for current app user."""
    db_handler = get_worker_db()
    with db_handler as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT local_path FROM image_cache WHERE profile_id = ?", (pk_id,)
        )
        row = cursor.fetchone()
        return row["local_path"] if row else None


def cache_image_path(pk_id: str, img_url: str, local_path: str) -> None:
    """creates an entry in the image_cache table for the current app user with the local path of a cached image"""
    db_handler = get_worker_db()
    with db_handler as conn:
        cursor = conn.cursor()
        # Why I am creating a separate img_id instead of using pk_id ?
        # It will enable me to track someone changing their profile picture (same pk_id but different img_url) and caching it as a new entry, without losing the old cached image until it's eventually cleaned up.
        img_id = f"{pk_id}_{hash(img_url)}"
        cursor.execute(
            "INSERT INTO image_cache (profile_id, img_id, img_url, local_path, create_date) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (pk_id, img_id, img_url, local_path),
        )
        conn.commit()


def store_account_info(instagram_profile: ii.FollowerUserRecord):
    pass

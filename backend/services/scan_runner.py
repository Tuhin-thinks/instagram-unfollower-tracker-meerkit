import threading
from datetime import datetime
from pathlib import Path

import get_current_followers as gcf
from backend.config import DATA_DIR

_scan_lock = threading.Lock()
_scan_state: dict = {
    "status": "idle",  # idle | running | error
    "started_at": None,
    "last_scan_id": None,
    "last_scan_at": None,
    "error": None,
}


def get_status() -> dict:
    return dict(_scan_state)


def start_scan() -> bool:
    """
    Start a scan in a background thread.
    Returns True if the scan was started, False if one is already in progress.
    """
    acquired = _scan_lock.acquire(blocking=False)
    if not acquired:
        return False

    _scan_state.update(
        {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "error": None,
        }
    )

    def _run() -> None:
        try:
            result = gcf.run_scan_for_api(DATA_DIR)
            _scan_state.update(
                {
                    "status": "idle",
                    "last_scan_id": result["scan_id"],
                    "last_scan_at": result["timestamp"],
                }
            )
        except Exception as exc:
            _scan_state.update({"status": "error", "error": str(exc)})
        finally:
            _scan_lock.release()

    threading.Thread(target=_run, daemon=True).start()
    return True

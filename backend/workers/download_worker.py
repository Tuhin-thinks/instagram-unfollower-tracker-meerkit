import threading
import time
import traceback

from backend.config import IMAGE_DOWNLOAD_DELAY_SECONDS
from backend.extensions import image_download_queue
from backend.services import db_service, downloader


def start_download_worker(app_user_id: str | None = None) -> None:
    def _run():
        db: db_service.SqliteDBHandler | None = None
        if app_user_id:
            db = db_service.init_worker_db(app_user_id)
        while True:
            item = image_download_queue.get()
            if item is None:  # poison pill to stop
                break
            try:
                _app_user_id, profile_pk_id, profile_pic_url = item
                if not db:
                    db = db_service.init_worker_db(_app_user_id)
                downloader.process_img_download(profile_pk_id, profile_pic_url)
            except Exception as _:
                traceback.print_exc()
            finally:
                image_download_queue.task_done()
            # delay to not overwhelm Instagram with too many requests in a short time, especially since some scans may have many followers
            time.sleep(IMAGE_DOWNLOAD_DELAY_SECONDS())

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    print("[Download worker] started.")

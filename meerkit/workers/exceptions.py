from __future__ import annotations

from meerkit.exceptions import MeerkitError


class WorkerError(MeerkitError):
    default_error_code = "worker_error"
    default_status_code = 500
    default_retryable = True


class ActionExecutionError(WorkerError):
    default_error_code = "action_execution_error"


class TaskProcessingError(WorkerError):
    default_error_code = "task_processing_error"


class DownloadProcessingError(WorkerError):
    default_error_code = "download_processing_error"

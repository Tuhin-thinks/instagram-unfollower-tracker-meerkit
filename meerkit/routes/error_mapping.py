from __future__ import annotations

import logging

from meerkit.exceptions import MeerkitError

logger = logging.getLogger(__name__)


def map_exception_to_response(exc: Exception) -> tuple[dict, int]:
    if isinstance(exc, MeerkitError):
        return exc.to_payload(), exc.status_code

    if isinstance(exc, ValueError):
        return {
            "error": str(exc),
            "code": "invalid_request",
            "type": "ValueError",
            "retryable": False,
        }, 400

    logger.exception("Unhandled exception at API boundary")
    return {
        "error": "Internal server error",
        "code": "internal_server_error",
        "type": exc.__class__.__name__,
        "retryable": False,
    }, 500

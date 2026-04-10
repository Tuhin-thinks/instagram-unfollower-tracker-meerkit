from flask import session

from meerkit.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)
from meerkit.services import auth_service


def get_active_context(
    instagram_user_id_override: str | None = None,
) -> tuple[str | None, dict | tuple[dict, int]]:
    """Return app user id and active instagram user, or an API error payload."""
    app_user_id = session.get("app_user_id")
    if not app_user_id:
        return None, (
            {
                "error": "Not logged in",
                "code": "auth_required",
                "type": "AuthenticationError",
                "retryable": False,
            },
            401,
        )

    instagram_user_id = instagram_user_id_override or session.get(
        "active_instagram_user_id"
    )
    if not instagram_user_id:
        instagram_user_id = auth_service.get_active_instagram_user_id(app_user_id)
        session["active_instagram_user_id"] = instagram_user_id
    if not instagram_user_id:
        return None, (
            {
                "error": "No active instagram user selected",
                "code": "active_instagram_user_required",
                "type": "ValidationError",
                "retryable": False,
            },
            400,
        )

    instagram_user = auth_service.get_instagram_user(app_user_id, instagram_user_id)
    if not instagram_user:
        return None, (
            {
                "error": "Instagram user not found",
                "code": "instagram_user_not_found",
                "type": "ResourceNotFoundError",
                "retryable": False,
            },
            404,
        )

    if instagram_user_id_override is None:
        session["active_instagram_user_id"] = instagram_user_id

    return app_user_id, instagram_user


def require_active_context(instagram_user_id_override: str | None = None) -> tuple[str, dict]:
    """Return active scope or raise typed exceptions for API boundaries."""
    app_user_id = session.get("app_user_id")
    if not app_user_id:
        raise AuthenticationError("Not logged in", error_code="auth_required")

    instagram_user_id = instagram_user_id_override or session.get(
        "active_instagram_user_id"
    )
    if not instagram_user_id:
        instagram_user_id = auth_service.get_active_instagram_user_id(app_user_id)
        session["active_instagram_user_id"] = instagram_user_id
    if not instagram_user_id:
        raise ValidationError(
            "No active instagram user selected",
            error_code="active_instagram_user_required",
            app_user_id=app_user_id,
        )

    instagram_user = auth_service.get_instagram_user(app_user_id, instagram_user_id)
    if not instagram_user:
        raise ResourceNotFoundError(
            "Instagram user not found",
            error_code="instagram_user_not_found",
            app_user_id=app_user_id,
            instagram_user_id=instagram_user_id,
        )

    if instagram_user_id_override is None:
        session["active_instagram_user_id"] = instagram_user_id

    return app_user_id, instagram_user


from typing import Any


class MeerkitError(Exception):
    """Base exception for all application-level errors."""

    default_error_code = "internal_error"
    default_status_code = 500
    default_retryable = False

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        status_code: int | None = None,
        retryable: bool | None = None,
        **context: Any,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.default_error_code
        self.status_code = status_code if status_code is not None else self.default_status_code
        self.retryable = (
            retryable if retryable is not None else self.default_retryable
        )
        self.context = {k: v for k, v in context.items() if v is not None}

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "error": self.message,
            "code": self.error_code,
            "type": self.__class__.__name__,
            "retryable": self.retryable,
        }
        if self.context:
            payload["context"] = self.context
        return payload


class ConfigurationError(MeerkitError):
    default_error_code = "configuration_error"
    default_status_code = 500
    default_retryable = False


class ValidationError(MeerkitError):
    default_error_code = "validation_error"
    default_status_code = 400
    default_retryable = False


class AuthenticationError(MeerkitError):
    default_error_code = "authentication_error"
    default_status_code = 401
    default_retryable = False


class AuthorizationError(MeerkitError):
    default_error_code = "authorization_error"
    default_status_code = 403
    default_retryable = False


class ResourceNotFoundError(MeerkitError):
    default_error_code = "resource_not_found"
    default_status_code = 404
    default_retryable = False


class ConflictError(MeerkitError):
    default_error_code = "conflict"
    default_status_code = 409
    default_retryable = False


class ExternalServiceError(MeerkitError):
    default_error_code = "external_service_error"
    default_status_code = 502
    default_retryable = True


class PersistenceError(MeerkitError):
    default_error_code = "persistence_error"
    default_status_code = 500
    default_retryable = True

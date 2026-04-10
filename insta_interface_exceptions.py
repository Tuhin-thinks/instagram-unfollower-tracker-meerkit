from __future__ import annotations

from meerkit.exceptions import ExternalServiceError, ValidationError


class InstaInterfaceError(ExternalServiceError):
    """Base exception for low-level Instagram interface operations."""

    default_error_code = "insta_interface_error"


class RelationshipFetchError(InstaInterfaceError):
    """Raised when relationship graph data cannot be parsed or is unavailable."""

    default_error_code = "relationship_fetch_error"

    def __init__(self, edge_name: str, reason: str) -> None:
        label = "followers" if "followed_by" in edge_name else "following"
        super().__init__(
            f"Could not fetch {label}: {reason}",
            edge_name=edge_name,
            relationship_label=label,
            reason=reason,
        )
        self.edge_name = edge_name
        self.label = label
        self.reason = reason


class ProfileLinkParseError(ValidationError):
    default_error_code = "profile_link_parse_error"


class TargetUserResolutionError(ValidationError):
    default_error_code = "target_user_resolution_error"


class InvalidFollowerDataError(ValidationError):
    default_error_code = "invalid_follower_data"


class InterfaceEntrypointError(ValidationError):
    default_error_code = "invalid_interface_entrypoint"

"""Custom domain exceptions for Mobile Application API Platform."""

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class MobileApiException(BusinessRuleViolation):
    """Base exception for mobile API platform errors."""
    pass


class VersionDeprecatedError(BusinessRuleViolation):
    """Raised when mobile client version is below the minimum required version."""

    def __init__(self, message: str = "This application version is no longer supported. Please update.") -> None:
        super().__init__(message=message, code="app_version_deprecated")


class SyncConflictError(ConflictError):
    """Raised when an offline mutation conflicts with the authoritative server entity state."""

    def __init__(self, message: str = "Offline sync conflict detected.") -> None:
        super().__init__(message=message, code="sync_conflict")

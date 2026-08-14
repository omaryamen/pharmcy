"""Custom domain exceptions for Enterprise SaaS Super Admin & Platform Operations Center."""

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class PlatformOpsException(BusinessRuleViolation):
    """Base domain exception for platform operations errors."""
    pass


class MaintenanceModeActiveError(BusinessRuleViolation):
    """Raised when non-whitelisted traffic accesses a system currently undergoing maintenance."""

    def __init__(self, message: str = "System is currently undergoing scheduled maintenance.") -> None:
        super().__init__(message=message, code="maintenance_mode_active")


class ImpersonationError(BusinessRuleViolation):
    """Raised when unauthorized or invalid tenant impersonation is attempted."""
    pass

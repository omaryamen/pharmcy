"""Custom domain exceptions for Enterprise Notifications & Automation Engine."""

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class NotificationException(BusinessRuleViolation):
    """Base exception for notification domain errors."""
    pass


class DuplicateEventError(ConflictError):
    """Raised when an event with identical idempotency key is submitted."""
    pass


class TemplateRenderingError(BusinessRuleViolation):
    """Raised when notification template rendering fails."""
    pass


class UnsafeWebhookUrlError(BusinessRuleViolation):
    """Raised when a webhook URL fails security SSRF validation."""
    pass

"""Custom domain exceptions for Enterprise SaaS Subscription, Billing & Licensing Platform."""

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class SaaSException(BusinessRuleViolation):
    """Base domain exception for SaaS billing errors."""
    pass


class EntitlementExceededError(BusinessRuleViolation):
    """Raised when a tenant attempts an operation exceeding their plan usage limit."""

    def __init__(self, feature_key: str, limit: int, current: int) -> None:
        message = f"Plan limit exceeded for '{feature_key}'. Allowed: {limit}, Current usage: {current}."
        super().__init__(message=message, code="entitlement_limit_exceeded")


class SubscriptionStateError(BusinessRuleViolation):
    """Raised when an invalid subscription lifecycle transition is attempted."""
    pass


class PaymentProcessingError(BusinessRuleViolation):
    """Raised when payment capture or tokenization fails."""
    pass

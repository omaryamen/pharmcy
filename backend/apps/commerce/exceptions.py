"""Custom domain exceptions for Enterprise Pharma E-Commerce & B2B Marketplace."""

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class CommerceException(BusinessRuleViolation):
    """Base domain exception for e-commerce operations."""
    pass


class StockUnavailableError(BusinessRuleViolation):
    """Raised when available stock is insufficient to fulfill an online order item."""

    def __init__(self, message: str = "Insufficient available inventory stock.") -> None:
        super().__init__(message=message, code="insufficient_commerce_stock")


class PrescriptionRequiredError(BusinessRuleViolation):
    """Raised when an order contains prescription-required drugs without approved prescription."""

    def __init__(self, message: str = "Order contains items that require an approved prescription.") -> None:
        super().__init__(message=message, code="prescription_required")


class CreditLimitExceededError(BusinessRuleViolation):
    """Raised when B2B credit order exceeds approved customer credit limit."""

    def __init__(self, message: str = "Order total exceeds customer approved credit limit.") -> None:
        super().__init__(message=message, code="credit_limit_exceeded")


class InvalidCouponError(BusinessRuleViolation):
    """Raised when a promotional coupon code is invalid, expired, or exceeds usage limits."""

    def __init__(self, message: str = "Invalid or expired coupon code.") -> None:
        super().__init__(message=message, code="invalid_coupon")

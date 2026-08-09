"""Validators for Enterprise Stock Adjustment & Stock Count module."""

from __future__ import annotations

from decimal import Decimal

from apps.stock_adjustment.exceptions import StockAdjustmentError


def validate_non_negative_quantity(quantity: Decimal | float | int, field_name: str = "Quantity") -> Decimal:
    val = Decimal(str(quantity))
    if val < Decimal("0.00"):
        raise StockAdjustmentError(f"{field_name} cannot be negative.")
    return val


def validate_user_not_same_as_counter(counter_user, approval_user, is_superuser: bool = False) -> None:
    if not is_superuser and counter_user and approval_user and counter_user.id == approval_user.id:
        from apps.stock_adjustment.exceptions import SelfApprovalForbiddenError
        raise SelfApprovalForbiddenError("Counters cannot approve their own high-variance physical counts.")

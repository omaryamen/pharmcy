"""Domain validators for Enterprise Stock Transfer module."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.stock_transfer.exceptions import (
    InsufficientTransferStockError,
    InvalidBatchForTransferError,
    SelfApprovalForbiddenError,
)


def validate_positive_quantity(value: Decimal | float | int) -> Decimal:
    """Ensure transfer quantity is strictly positive (> 0)."""
    dec_val = Decimal(str(value))
    if dec_val <= Decimal("0"):
        raise ValidationError(_("Transfer quantity must be greater than zero."))
    return dec_val


def validate_non_negative_quantity(value: Decimal | float | int) -> Decimal:
    """Ensure quantity is non-negative (>= 0)."""
    dec_val = Decimal(str(value))
    if dec_val < Decimal("0"):
        raise ValidationError(_("Quantity cannot be negative."))
    return dec_val


def validate_batch_eligible_for_transfer(batch: Any) -> None:
    """Verify that a batch is active, non-expired, non-recalled, non-quarantined, and non-blocked."""
    if not batch:
        return

    is_expired = getattr(batch, "is_expired", False)
    if not is_expired and getattr(batch, "expiry_date", None):
        is_expired = batch.expiry_date <= timezone.now().date()

    status_val = getattr(batch, "status", getattr(batch, "batch_status", "active"))

    if is_expired or status_val == "expired":
        raise InvalidBatchForTransferError(_("Batch %s is expired and cannot be transferred.") % getattr(batch, "batch_number", ""))

    if status_val in ["quarantine", "recalled", "blocked", "depleted", "archived"]:
        raise InvalidBatchForTransferError(
            _("Batch %s has status '%s' and cannot be transferred.") % (getattr(batch, "batch_number", ""), status_val)
        )


def validate_approval_separation_of_duties(requested_by: Any, approving_user: Any, is_superuser: bool = False) -> None:
    """Verify separation of duties: requester cannot approve their own transfer unless superuser."""
    if is_superuser:
        return
    if requested_by and approving_user and getattr(requested_by, "id", None) == getattr(approving_user, "id", None):
        raise SelfApprovalForbiddenError(_("Transfer requester cannot approve their own transfer request."))

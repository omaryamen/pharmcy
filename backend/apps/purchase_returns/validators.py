"""Domain validators for Enterprise Purchase Returns & Supplier Returns."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.purchase_returns.exceptions import (
    ExceedsReturnableQuantityError,
    ReturnSelfApprovalForbiddenError,
)


def validate_return_eligibility(
    medicine: Any,
    batch: Any,
    requested_quantity: Decimal | float | int,
    available_stock_quantity: Decimal | float | int,
) -> Decimal:
    """Ensure requested return quantity is valid and does not exceed available physical stock balance."""
    req_qty = Decimal(str(requested_quantity))
    avail_qty = Decimal(str(available_stock_quantity))

    if req_qty <= Decimal("0"):
        raise ValidationError(_("Return quantity must be greater than zero."))

    if batch.medicine_id != medicine.id:
        raise ValidationError(_("Batch %s does not belong to medicine %s.") % (batch.batch_number, medicine.english_name))

    if req_qty > avail_qty:
        raise ExceedsReturnableQuantityError(
            _("Requested return quantity %s exceeds available stock balance (%s) for batch %s.")
            % (req_qty, avail_qty, batch.batch_number)
        )

    return req_qty


def validate_return_approval_separation_of_duties(
    requested_by: Any, approving_user: Any, is_superuser: bool = False
) -> None:
    """Enforce separation of duties: Return requester cannot approve their own return unless superuser."""
    if is_superuser:
        return
    if requested_by and approving_user and getattr(requested_by, "id", None) == getattr(approving_user, "id", None):
        raise ReturnSelfApprovalForbiddenError(_("Purchase Return requester cannot approve their own return request."))

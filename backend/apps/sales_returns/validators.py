"""Domain validators for Enterprise Customer Sales Returns & Refund Management."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.sales_returns.exceptions import (
    ExceedsReturnableQuantityError,
    ReturnApprovalSelfForbiddenError,
)


def validate_returnable_quantity(
    requested_quantity: Decimal | float | int,
    original_sold_quantity: Decimal | float | int,
    previously_returned_quantity: Decimal | float | int,
) -> Decimal:
    """Ensure requested return quantity does not exceed available returnable quantity."""
    req = Decimal(str(requested_quantity))
    orig = Decimal(str(original_sold_quantity))
    prev = Decimal(str(previously_returned_quantity))
    returnable = orig - prev

    if req > returnable:
        raise ExceedsReturnableQuantityError(
            _("Requested return quantity (%s) exceeds remaining returnable quantity (%s).") % (req, returnable)
        )
    return returnable


def validate_return_approval_separation_of_duties(creator: Any, approver: Any) -> None:
    """Enforce separation of duties: return requester cannot approve their own request."""
    if creator and approver and creator.pk == approver.pk:
        raise ReturnApprovalSelfForbiddenError(_("Customer return requester cannot approve their own return request."))

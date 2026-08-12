"""Domain validators for Enterprise Customer Accounts Receivable (AR)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils.translation import gettext_lazy as _

from apps.accounts_receivable.exceptions import (
    CreditLimitExceededError,
    ExceedsOutstandingBalanceError,
    SelfApprovalForbiddenError,
)


def validate_credit_limit(customer: Any, requested_credit_amount: Decimal | float | int) -> None:
    """Validate that requested credit sale does not exceed customer's configured credit limit."""
    if not getattr(customer, "credit_allowed", True):
        raise CreditLimitExceededError(_("Credit sales are not allowed for customer '%s'.") % customer.english_name)

    req = Decimal(str(requested_credit_amount))
    limit = Decimal(str(getattr(customer, "credit_limit", "0.00")))
    current_balance = Decimal(str(getattr(customer, "current_balance", "0.00")))

    # Customer current_balance represents total credit extended (debt)
    potential_balance = current_balance + req
    if limit > Decimal("0.00") and potential_balance > limit:
        raise CreditLimitExceededError(
            _("Requested credit sale ${:,.2f} increases customer debt to ${:,.2f}, exceeding credit limit of ${:,.2f}.").format(
                req, potential_balance, limit
            )
        )


def validate_allocation_amount(allocated_amount: Decimal | float | int, receivable_outstanding: Decimal | float | int) -> Decimal:
    """Ensure allocation amount does not exceed net outstanding receivable obligation."""
    alloc = Decimal(str(allocated_amount))
    outstanding = Decimal(str(receivable_outstanding))

    if alloc <= Decimal("0.0000"):
        raise ExceedsOutstandingBalanceError(_("Allocation amount must be greater than zero."))

    if alloc > outstanding:
        raise ExceedsOutstandingBalanceError(
            _("Allocated amount ${:,.2f} exceeds net outstanding receivable balance ${:,.2f}.").format(alloc, outstanding)
        )
    return alloc


def validate_ar_separation_of_duties(creator: Any, approver: Any) -> None:
    """Enforce separation of duties: creator cannot approve own adjustment or write-off."""
    if creator and approver and creator.pk == approver.pk:
        raise SelfApprovalForbiddenError(_("Separation of duties violation: creator cannot approve own AR transaction."))

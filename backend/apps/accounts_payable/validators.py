"""Domain validators and due-date calculator for Accounts Payable."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.accounts_payable.exceptions import (
    ExceedsOutstandingBalanceError,
    PaymentSelfApprovalForbiddenError,
)
from apps.accounts_payable.models.enums import PaymentTerms


def calculate_due_date_from_terms(
    invoice_date: date, payment_terms: str, custom_due_date: date | None = None
) -> date:
    """Date-safe calculation of invoice due date based on PaymentTerms enum."""
    if payment_terms == PaymentTerms.CUSTOM and custom_due_date:
        return custom_due_date

    days_map = {
        PaymentTerms.CASH: 0,
        PaymentTerms.NET_7: 7,
        PaymentTerms.NET_15: 15,
        PaymentTerms.NET_30: 30,
        PaymentTerms.NET_45: 45,
        PaymentTerms.NET_60: 60,
        PaymentTerms.NET_90: 90,
    }
    days = days_map.get(payment_terms, 30)
    return invoice_date + timedelta(days=days)


def validate_invoice_approval_separation_of_duties(
    creator: Any, approver: Any, is_superuser: bool = False
) -> None:
    """Enforce separation of duties: Invoice/Payment creator cannot approve their own document."""
    if is_superuser:
        return
    if creator and approver and getattr(creator, "id", None) == getattr(approver, "id", None):
        raise PaymentSelfApprovalForbiddenError(
            _("Invoice or Payment creator cannot approve their own financial document.")
        )


def validate_payment_amount(
    amount: Decimal | float | int, outstanding_amount: Decimal | float | int
) -> Decimal:
    """Ensure payment or credit application does not exceed outstanding balance."""
    pmt_amt = Decimal(str(amount))
    out_amt = Decimal(str(outstanding_amount))

    if pmt_amt <= Decimal("0.0000"):
        raise ValidationError(_("Payment amount must be greater than zero."))

    if pmt_amt > out_amt:
        raise ExceedsOutstandingBalanceError(
            _("Payment amount (%s) exceeds outstanding payable balance (%s).") % (pmt_amt, out_amt)
        )

    return pmt_amt

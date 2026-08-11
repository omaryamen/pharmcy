"""Domain validators for Enterprise POS & Sales Management."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.inventory.models.enums import BatchStatus
from apps.sales.exceptions import (
    ExceedsCustomerCreditLimitError,
    IneligibleBatchForSaleError,
)


def validate_batch_eligibility_for_sale(batch: Any) -> None:
    """Ensure selected medicine batch is eligible for retail sale (Active, non-expired, non-recalled, non-quarantined)."""
    today = timezone.now().date()

    if batch.status == BatchStatus.RECALLED:
        raise IneligibleBatchForSaleError(_("Batch %s is RECALLED and cannot be sold.") % batch.batch_number)

    if batch.status in [BatchStatus.QUARANTINE, BatchStatus.BLOCKED]:
        raise IneligibleBatchForSaleError(_("Batch %s is in status '%s' and cannot be sold.") % (batch.batch_number, batch.status))

    if batch.expiry_date <= today:
        raise IneligibleBatchForSaleError(_("Batch %s expired on %s and cannot be sold.") % (batch.batch_number, batch.expiry_date))


def validate_customer_credit_sale(customer: Any, credit_amount: Decimal | float | int) -> None:
    """Ensure customer is active, permits credit sales, and has sufficient available credit limit."""
    amt = Decimal(str(credit_amount))

    if getattr(customer, "status", "active") != "active":
        name = getattr(customer, "english_name", "") or getattr(customer, "first_name", "Customer")
        raise ValidationError(_("Customer %s is inactive or suspended.") % name)

    credit_allowed = getattr(customer, "credit_allowed", True) and getattr(customer, "allow_credit", True)
    if not credit_allowed:
        name = getattr(customer, "english_name", "") or getattr(customer, "first_name", "Customer")
        raise ValidationError(_("Credit sales are not permitted for customer %s.") % name)

    credit_limit = getattr(customer, "credit_limit", Decimal("0.0000"))
    current_balance = getattr(customer, "current_balance", Decimal("0.0000"))
    available_credit = credit_limit - current_balance

    if amt > available_credit and credit_limit > Decimal("0.0000"):
        raise ExceedsCustomerCreditLimitError(
            _("Credit sale amount (%s) exceeds customer available credit limit (%s).") % (amt, available_credit)
        )


def calculate_cash_change(tendered_amount: Decimal | float | int, grand_total: Decimal | float | int) -> Decimal:
    """Calculate cash change returned to customer."""
    t_amt = Decimal(str(tendered_amount))
    g_tot = Decimal(str(grand_total))

    if t_amt < g_tot:
        raise ValidationError(_("Tendered cash amount (%s) is less than invoice total (%s).") % (t_amt, g_tot))

    return t_amt - g_tot

"""Domain validators for Enterprise General Ledger & Double-Entry Accounting."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils.translation import gettext_lazy as _

from apps.general_ledger.exceptions import (
    ControlAccountPostingForbiddenError,
    PeriodClosedError,
    UnbalancedJournalError,
)
from apps.general_ledger.models.enums import PeriodStatus


def validate_double_entry_balance(total_debit: Decimal | float | int, total_credit: Decimal | float | int) -> None:
    """CRITICAL RULE: Ensure Total Debits equal Total Credits for double-entry accounting integrity."""
    deb = Decimal(str(total_debit))
    cred = Decimal(str(total_credit))

    if deb != cred:
        raise UnbalancedJournalError(
            _("Unbalanced journal transaction: Total Debits (${:,.4f}) != Total Credits (${:,.4f}). Difference: ${:,.4f}.").format(
                deb, cred, deb - cred
            )
        )

    if deb <= Decimal("0.0000") or cred <= Decimal("0.0000"):
        raise UnbalancedJournalError(_("Journal transaction total debit and credit amounts must be greater than zero."))


def validate_period_is_open(period: Any) -> None:
    """Ensure posting date falls within an open accounting period."""
    if not period or period.status != PeriodStatus.OPEN:
        raise PeriodClosedError(_("Cannot post journal to accounting period '%s' in status '%s'.") % (getattr(period, "name", "Unknown"), getattr(period, "status", "CLOSED")))


def validate_account_postable(account: Any) -> None:
    """Ensure target account is active and not a non-postable summary control parent account."""
    if getattr(account, "is_control_account", False):
        raise ControlAccountPostingForbiddenError(
            _("Direct journal posting to summary control account '%s (%s)' is forbidden.")
            % (getattr(account, "account_name", ""), getattr(account, "account_code", ""))
        )
    if getattr(account, "status", "active") != "active":
        raise ControlAccountPostingForbiddenError(
            _("Chart of Account '%s' is inactive and cannot accept postings.") % getattr(account, "account_code", "")
        )

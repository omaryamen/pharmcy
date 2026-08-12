"""GLReconciliationService auditing General Ledger entries against subledger operational modules."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db.models import Sum

from apps.accounts_payable.models import AccountsPayableEntry
from apps.accounts_receivable.models import CustomerReceivable
from apps.companies.models import Company
from apps.general_ledger.models import JournalEntry, JournalEntryLine, JournalStatus
from apps.general_ledger.selectors import GLSelector
from apps.sales.models import SalesInvoice

logger = logging.getLogger(__name__)


class GLReconciliationService:
    """Service layer executing comprehensive financial reconciliation audits across operational subledgers and General Ledger control accounts."""

    def __init__(self) -> None:
        self.selector = GLSelector()

    def audit_general_ledger_integrity(self, tenant: Any, company: Company) -> dict[str, Any]:
        """Perform comprehensive accounting audit (Trial Balance balance, AR Control vs AR Subledger, AP Control vs AP Subledger)."""
        tb = self.selector.get_trial_balance(tenant, str(company.pk))

        # 1. Trial Balance Check
        tb_is_balanced = tb["is_balanced"]
        tb_discrepancy = tb["total_debit"] - tb["total_credit"]

        # 2. AR Subledger vs AR Control Account Check
        subledger_ar_outstanding = (
            CustomerReceivable.objects.filter(tenant=tenant, company=company)
            .aggregate(val=Sum("outstanding_amount"))["val"]
            or Decimal("0.0000")
        )

        ar_acc = (
            JournalEntryLine.objects.filter(
                tenant=tenant,
                journal_entry__company=company,
                journal_entry__status=JournalStatus.POSTED,
                account__account_code="1300",
            )
        )
        gl_ar_balance = (ar_acc.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000")) - (ar_acc.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000"))
        ar_discrepancy = subledger_ar_outstanding - gl_ar_balance

        # 3. AP Subledger vs AP Control Account Check
        subledger_ap_outstanding = (
            AccountsPayableEntry.objects.filter(tenant=tenant, company=company)
            .aggregate(val=Sum("outstanding_amount"))["val"]
            or Decimal("0.0000")
        )

        ap_acc = (
            JournalEntryLine.objects.filter(
                tenant=tenant,
                journal_entry__company=company,
                journal_entry__status=JournalStatus.POSTED,
                account__account_code="2100",
            )
        )
        gl_ap_balance = (ap_acc.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000")) - (ap_acc.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000"))
        ap_discrepancy = subledger_ap_outstanding - gl_ap_balance

        is_healthy = tb_is_balanced and (ar_discrepancy == Decimal("0.0000")) and (ap_discrepancy == Decimal("0.0000"))

        return {
            "company_id": str(company.pk),
            "company_name": company.legal_name,
            "trial_balance": {
                "total_debit": tb["total_debit"],
                "total_credit": tb["total_credit"],
                "is_balanced": tb_is_balanced,
                "discrepancy": tb_discrepancy,
            },
            "accounts_receivable": {
                "subledger_total": subledger_ar_outstanding,
                "gl_control_total": gl_ar_balance,
                "discrepancy": ar_discrepancy,
                "is_reconciled": ar_discrepancy == Decimal("0.0000"),
            },
            "accounts_payable": {
                "subledger_total": subledger_ap_outstanding,
                "gl_control_total": gl_ap_balance,
                "discrepancy": ap_discrepancy,
                "is_reconciled": ap_discrepancy == Decimal("0.0000"),
            },
            "is_system_healthy": is_healthy,
        }

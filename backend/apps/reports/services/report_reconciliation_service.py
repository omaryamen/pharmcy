"""ReportReconciliationService validating cross-subledger financial integrity between operational modules and the General Ledger."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from apps.accounts_payable.selectors import AccountsPayableSelector
from apps.accounts_receivable.selectors import ReceivableSelector
from apps.cash_and_bank.selectors import TreasurySelector
from apps.expenses.selectors import ExpenseSelector
from apps.general_ledger.selectors import GLSelector
from apps.general_ledger.services import GLReconciliationService

logger = logging.getLogger(__name__)


class ReportReconciliationService:
    """Service layer auditing platform-wide financial reconciliation between operational subledgers and the General Ledger."""

    def __init__(
        self,
        gl_reconciliation_service: GLReconciliationService | None = None,
        treasury_selector: TreasurySelector | None = None,
        expense_selector: ExpenseSelector | None = None,
    ) -> None:
        self.gl_reconciliation_service = gl_reconciliation_service or GLReconciliationService()
        self.treasury_selector = treasury_selector or TreasurySelector()
        self.expense_selector = expense_selector or ExpenseSelector()

    def run_platform_reconciliation_audit(self, tenant: Any, company: Any) -> dict[str, Any]:
        """Audit subledgers against control GL accounts and report discrepancies explicitly."""
        ar_audit = self.gl_reconciliation_service.reconcile_ar_control_account(tenant, company)
        ap_audit = self.gl_reconciliation_service.reconcile_ap_control_account(tenant, company)

        treasury_summary = self.treasury_selector.get_treasury_summary(tenant, company_id=str(company.pk))
        expense_summary = self.expense_selector.get_expense_summary(tenant, company_id=str(company.pk))

        total_discrepant_modules = 0
        if ar_audit["status"] != "reconciled":
            total_discrepant_modules += 1
        if ap_audit["status"] != "reconciled":
            total_discrepant_modules += 1

        status_str = "reconciled" if total_discrepant_modules == 0 else "discrepancy_detected"

        logger.info(f"Ran Platform Reconciliation Audit for company {company.legal_name} -> Status: {status_str}")
        return {
            "platform_status": status_str,
            "total_discrepant_modules": total_discrepant_modules,
            "ar_subledger_reconciliation": ar_audit,
            "ap_subledger_reconciliation": ap_audit,
            "treasury_liquidity_summary": treasury_summary,
            "operating_expenses_summary": expense_summary,
        }

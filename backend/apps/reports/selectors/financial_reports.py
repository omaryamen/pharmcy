"""FinancialReportSelector delegating to authoritative General Ledger, AR, AP, Cash, and Expense selectors."""

from __future__ import annotations

from typing import Any

from apps.accounts_receivable.selectors import ReceivableSelector
from apps.cash_and_bank.selectors import TreasurySelector
from apps.expenses.selectors import ExpenseSelector
from apps.general_ledger.selectors import GLSelector
from apps.reports.selectors.dto import ReportFilterDTO


class FinancialReportSelector:
    """Master financial reporting selector orchestrating authoritative GL, AR, AP, Treasury, and Expense reports."""

    def __init__(
        self,
        gl_selector: GLSelector | None = None,
        ar_selector: ReceivableSelector | None = None,
        treasury_selector: TreasurySelector | None = None,
        expense_selector: ExpenseSelector | None = None,
    ) -> None:
        self.gl_selector = gl_selector or GLSelector()
        self.ar_selector = ar_selector or ReceivableSelector()
        self.treasury_selector = treasury_selector or TreasurySelector()
        self.expense_selector = expense_selector or ExpenseSelector()

    def get_trial_balance(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Trial Balance from General Ledger (IMP-029)."""
        start_date, end_date = filters.resolve_dates()
        return self.gl_selector.get_trial_balance(
            tenant=filters.tenant,
            company_id=filters.company_id,
            as_of_date=end_date,
        )

    def get_profit_and_loss(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Profit & Loss statement from General Ledger (IMP-029)."""
        start_date, end_date = filters.resolve_dates()
        return self.gl_selector.get_profit_and_loss(
            tenant=filters.tenant,
            company_id=filters.company_id,
            start_date=start_date,
            end_date=end_date,
        )

    def get_balance_sheet(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Balance Sheet from General Ledger (IMP-029)."""
        start_date, end_date = filters.resolve_dates()
        return self.gl_selector.get_balance_sheet(
            tenant=filters.tenant,
            company_id=filters.company_id,
            as_of_date=end_date,
        )

    def get_ar_aging(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Customer AR Aging buckets from Accounts Receivable (IMP-028)."""
        return self.ar_selector.get_ar_aging_summary(
            tenant=filters.tenant,
            company_id=filters.company_id,
            customer_id=filters.customer_id,
        )

    def get_cash_treasury_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Treasury liquidity summary from Cash & Bank (IMP-030)."""
        return self.treasury_selector.get_treasury_summary(
            tenant=filters.tenant,
            company_id=filters.company_id,
        )

    def get_expense_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Fetch authoritative Expense summary from Expense Management (IMP-031)."""
        return self.expense_selector.get_expense_summary(
            tenant=filters.tenant,
            company_id=filters.company_id,
        )

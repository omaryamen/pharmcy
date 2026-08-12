"""Query selector layer for Cash, Bank, Sessions, and Treasury reporting."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q, QuerySet, Sum

from apps.cash_and_bank.models import (
    BankAccount,
    BankReconciliation,
    BankTransaction,
    CashAccount,
    CashDeposit,
    CashMovement,
    CashTransfer,
    CashVariance,
    CashWithdrawal,
    ReconciliationMatchStatus,
)
from apps.sales.models import RegisterSession


class TreasurySelector:
    """Selector serving Treasury management dashboards, cash position lookups, and bank statement queries."""

    def list_cash_accounts(self, tenant: Any, *, company_id: str | None = None, branch_id: str | None = None) -> QuerySet[CashAccount]:
        qs = CashAccount.objects.filter(tenant=tenant).select_related("company", "branch", "gl_account")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def list_bank_accounts(self, tenant: Any, *, company_id: str | None = None, branch_id: str | None = None) -> QuerySet[BankAccount]:
        qs = BankAccount.objects.filter(tenant=tenant).select_related("company", "branch", "gl_account")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def list_bank_transactions(
        self,
        tenant: Any,
        *,
        bank_account_id: str | None = None,
        reconciliation_status: str | None = None,
        start_date: Any = None,
        end_date: Any = None,
    ) -> QuerySet[BankTransaction]:
        qs = BankTransaction.objects.filter(tenant=tenant).select_related("bank_account")
        if bank_account_id:
            qs = qs.filter(bank_account_id=bank_account_id)
        if reconciliation_status:
            qs = qs.filter(reconciliation_status=reconciliation_status)
        if start_date:
            qs = qs.filter(transaction_date__gte=start_date)
        if end_date:
            qs = qs.filter(transaction_date__lte=end_date)
        return qs

    def get_treasury_summary(self, tenant: Any, *, company_id: str | None = None) -> dict[str, Any]:
        """Calculate high-level Treasury liquidity overview."""
        cash_qs = self.list_cash_accounts(tenant, company_id=company_id)
        bank_qs = self.list_bank_accounts(tenant, company_id=company_id)

        total_cash = cash_qs.aggregate(val=Sum("current_balance"))["val"] or Decimal("0.0000")
        total_bank = bank_qs.aggregate(val=Sum("current_balance"))["val"] or Decimal("0.0000")
        total_liquidity = total_cash + total_bank

        open_sessions = RegisterSession.objects.filter(tenant=tenant, status="open").count()
        unmatched_bank_tx = BankTransaction.objects.filter(tenant=tenant, reconciliation_status=ReconciliationMatchStatus.UNMATCHED).count()
        unresolved_variances = CashVariance.objects.filter(tenant=tenant, status="pending").count()

        return {
            "total_cash_balance": total_cash,
            "total_bank_balance": total_bank,
            "total_liquidity": total_liquidity,
            "open_register_sessions_count": open_sessions,
            "unmatched_bank_transactions_count": unmatched_bank_tx,
            "unresolved_cash_variances_count": unresolved_variances,
        }

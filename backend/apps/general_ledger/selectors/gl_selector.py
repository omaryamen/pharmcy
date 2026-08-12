"""Query selector layer for Chart of Accounts, General Ledger, Trial Balance, Profit & Loss, and Balance Sheet reporting."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q, QuerySet, Sum
from django.utils import timezone

from apps.general_ledger.models import (
    AccountSubtype,
    AccountType,
    ChartOfAccount,
    JournalEntry,
    JournalEntryLine,
    JournalStatus,
)


class GLSelector:
    """Selector serving double-entry General Ledger running balances, Trial Balance, P&L, and Balance Sheet."""

    def list_accounts(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        account_type: str | None = None,
        search: str | None = None,
    ) -> QuerySet[ChartOfAccount]:
        qs = ChartOfAccount.objects.filter(tenant=tenant).select_related("company", "branch", "parent")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if account_type:
            qs = qs.filter(account_type=account_type)
        if search:
            qs = qs.filter(
                Q(account_code__icontains=search)
                | Q(account_name__icontains=search)
                | Q(english_name__icontains=search)
                | Q(arabic_name__icontains=search)
            )
        return qs

    def list_journals(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        status: str | None = None,
        reference_type: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
    ) -> QuerySet[JournalEntry]:
        qs = JournalEntry.objects.filter(tenant=tenant).select_related("company", "branch", "accounting_period", "posted_by").prefetch_related("lines__account")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if status:
            qs = qs.filter(status=status)
        if reference_type:
            qs = qs.filter(reference_type=reference_type)
        if source_module:
            qs = qs.filter(source_module=source_module)
        if search:
            qs = qs.filter(
                Q(journal_number__icontains=search)
                | Q(description__icontains=search)
                | Q(reference_number__icontains=search)
            )
        return qs

    def get_general_ledger_account_statement(
        self,
        tenant: Any,
        account_id: str,
        *,
        start_date: Any = None,
        end_date: Any = None,
    ) -> dict[str, Any]:
        """Calculate running debit/credit balance ledger for a specific ChartOfAccount."""
        account = ChartOfAccount.objects.get(pk=account_id, tenant=tenant)
        lines = JournalEntryLine.objects.filter(tenant=tenant, account=account, journal_entry__status=JournalStatus.POSTED).select_related("journal_entry")

        if start_date:
            lines = lines.filter(journal_entry__posting_date__gte=start_date)
        if end_date:
            lines = lines.filter(journal_entry__posting_date__lte=end_date)

        running_balance = Decimal("0.0000")
        ledger_entries = []

        for line in lines.order_by("journal_entry__posting_date", "created_at"):
            deb = line.debit
            cred = line.credit

            # Normal debit balance accounts vs credit balance accounts
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE, AccountType.COST_OF_GOODS_SOLD]:
                running_balance += (deb - cred)
            else:
                running_balance += (cred - deb)

            ledger_entries.append({
                "journal_number": line.journal_entry.journal_number,
                "posting_date": line.journal_entry.posting_date,
                "reference": line.journal_entry.reference_number,
                "description": line.description or line.journal_entry.description,
                "debit": deb,
                "credit": cred,
                "running_balance": running_balance,
            })

        return {
            "account_id": str(account.pk),
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "closing_balance": running_balance,
            "entries": ledger_entries,
        }

    def get_trial_balance(
        self,
        tenant: Any,
        company_id: str,
        *,
        as_of_date: Any = None,
    ) -> dict[str, Any]:
        """Calculate authoritatively balanced Trial Balance report (Total Debits == Total Credits)."""
        accounts = ChartOfAccount.objects.filter(tenant=tenant, company_id=company_id, is_control_account=False)

        lines = JournalEntryLine.objects.filter(tenant=tenant, journal_entry__company_id=company_id, journal_entry__status=JournalStatus.POSTED)
        if as_of_date:
            lines = lines.filter(journal_entry__posting_date__lte=as_of_date)

        total_debit = Decimal("0.0000")
        total_credit = Decimal("0.0000")
        account_balances = []

        for acc in accounts:
            acc_lines = lines.filter(account=acc)
            deb_sum = acc_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000")
            cred_sum = acc_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000")

            if deb_sum == Decimal("0.0000") and cred_sum == Decimal("0.0000"):
                continue

            total_debit += deb_sum
            total_credit += cred_sum

            account_balances.append({
                "account_id": str(acc.pk),
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "debit": deb_sum,
                "credit": cred_sum,
                "net_balance": deb_sum - cred_sum,
            })

        return {
            "as_of_date": as_of_date or timezone.now().date(),
            "total_debit": total_debit,
            "total_credit": total_credit,
            "is_balanced": total_debit == total_credit,
            "accounts": account_balances,
        }

    def get_profit_and_loss(
        self,
        tenant: Any,
        company_id: str,
        *,
        start_date: Any = None,
        end_date: Any = None,
    ) -> dict[str, Any]:
        """Calculate Income Statement (Profit & Loss) strictly from posted General Ledger entries."""
        lines = JournalEntryLine.objects.filter(tenant=tenant, journal_entry__company_id=company_id, journal_entry__status=JournalStatus.POSTED)
        if start_date:
            lines = lines.filter(journal_entry__posting_date__gte=start_date)
        if end_date:
            lines = lines.filter(journal_entry__posting_date__lte=end_date)

        rev_lines = lines.filter(account__account_type=AccountType.REVENUE)
        cogs_lines = lines.filter(account__account_type=AccountType.COST_OF_GOODS_SOLD)
        exp_lines = lines.filter(account__account_type=AccountType.EXPENSE)

        total_revenue = (rev_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000")) - (rev_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000"))
        total_cogs = (cogs_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000")) - (cogs_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000"))
        gross_profit = total_revenue - total_cogs

        total_expenses = (exp_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000")) - (exp_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000"))
        net_profit = gross_profit - total_expenses

        return {
            "total_revenue": total_revenue,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
        }

    def get_balance_sheet(
        self,
        tenant: Any,
        company_id: str,
        *,
        as_of_date: Any = None,
    ) -> dict[str, Any]:
        """Calculate Balance Sheet strictly from posted General Ledger entries (Assets = Liabilities + Equity)."""
        lines = JournalEntryLine.objects.filter(tenant=tenant, journal_entry__company_id=company_id, journal_entry__status=JournalStatus.POSTED)
        if as_of_date:
            lines = lines.filter(journal_entry__posting_date__lte=as_of_date)

        asset_lines = lines.filter(account__account_type=AccountType.ASSET)
        liab_lines = lines.filter(account__account_type=AccountType.LIABILITY)
        equity_lines = lines.filter(account__account_type=AccountType.EQUITY)

        total_assets = (asset_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000")) - (asset_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000"))
        total_liabilities = (liab_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000")) - (liab_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000"))
        total_equity = (equity_lines.aggregate(val=Sum("credit"))["val"] or Decimal("0.0000")) - (equity_lines.aggregate(val=Sum("debit"))["val"] or Decimal("0.0000"))

        pnl = self.get_profit_and_loss(tenant, company_id, end_date=as_of_date)
        net_retained_earnings = pnl["net_profit"]
        total_equity_with_earnings = total_equity + net_retained_earnings

        return {
            "as_of_date": as_of_date or timezone.now().date(),
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity_with_earnings,
            "is_balanced": total_assets == (total_liabilities + total_equity_with_earnings),
        }

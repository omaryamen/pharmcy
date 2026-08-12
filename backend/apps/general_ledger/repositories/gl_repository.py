"""Repository layer for ChartOfAccount, JournalEntry, and AccountingPeriod persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.general_ledger.models import AccountingPeriod, ChartOfAccount, JournalEntry


class ChartOfAccountRepository:
    """Repository encapsulating persistence for ChartOfAccount entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[ChartOfAccount]:
        return ChartOfAccount.objects.filter(tenant=tenant)

    def find_by_code(self, tenant: Any, company_id: str, code: str) -> ChartOfAccount | None:
        return self.get_queryset(tenant).filter(company_id=company_id, account_code=code).first()

    def create(self, tenant: Any, **kwargs: Any) -> ChartOfAccount:
        return ChartOfAccount.objects.create(tenant=tenant, **kwargs)


class JournalEntryRepository:
    """Repository encapsulating persistence for JournalEntry entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(tenant=tenant)

    def find_by_idempotency_key(self, tenant: Any, key: str) -> JournalEntry | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> JournalEntry:
        return JournalEntry.objects.create(tenant=tenant, **kwargs)


class AccountingPeriodRepository:
    """Repository encapsulating persistence for AccountingPeriod entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[AccountingPeriod]:
        return AccountingPeriod.objects.filter(tenant=tenant)

    def find_open_period(self, tenant: Any, company_id: str, posting_date: Any) -> AccountingPeriod | None:
        return (
            self.get_queryset(tenant)
            .filter(
                company_id=company_id,
                start_date__lte=posting_date,
                end_date__gte=posting_date,
                status="open",
            )
            .first()
        )

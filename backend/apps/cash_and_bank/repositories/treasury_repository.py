"""Repository layer for CashAccount, BankAccount, and BankTransaction persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.cash_and_bank.models import BankAccount, BankTransaction, CashAccount


class CashAccountRepository:
    """Repository encapsulating persistence for CashAccount entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[CashAccount]:
        return CashAccount.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, account_id: str) -> CashAccount | None:
        return self.get_queryset(tenant).filter(pk=account_id).first()


class BankAccountRepository:
    """Repository encapsulating persistence for BankAccount entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[BankAccount]:
        return BankAccount.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, account_id: str) -> BankAccount | None:
        return self.get_queryset(tenant).filter(pk=account_id).first()


class BankTransactionRepository:
    """Repository encapsulating persistence for BankTransaction entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[BankTransaction]:
        return BankTransaction.objects.filter(tenant=tenant)

    def find_by_hash(self, tenant: Any, bank_account_id: str, import_hash: str) -> BankTransaction | None:
        return self.get_queryset(tenant).filter(bank_account_id=bank_account_id, import_hash=import_hash).first()

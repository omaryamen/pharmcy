"""Repository layer for PurchaseReturn persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.purchase_returns.models import (
    PurchaseReturn,
    PurchaseReturnLine,
    ReturnDiscrepancy,
    SupplierCreditNote,
)


class PurchaseReturnRepository:
    """Repository encapsulating persistence operations for PurchaseReturn."""

    def get_queryset(self, tenant: Any) -> QuerySet[PurchaseReturn]:
        return PurchaseReturn.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, return_id: str) -> PurchaseReturn | None:
        return self.get_queryset(tenant).filter(pk=return_id).first()

    def find_by_number(self, tenant: Any, number: str) -> PurchaseReturn | None:
        return self.get_queryset(tenant).filter(return_number=number).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> PurchaseReturn | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseReturn:
        return PurchaseReturn.objects.create(tenant=tenant, **kwargs)

    def update(self, purchase_return: PurchaseReturn, **kwargs: Any) -> PurchaseReturn:
        for field, value in kwargs.items():
            setattr(purchase_return, field, value)
        purchase_return.save()
        return purchase_return


class PurchaseReturnLineRepository:
    """Repository encapsulating persistence operations for PurchaseReturnLine."""

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseReturnLine:
        return PurchaseReturnLine.objects.create(tenant=tenant, **kwargs)


class ReturnDiscrepancyRepository:
    """Repository encapsulating persistence operations for ReturnDiscrepancy."""

    def create(self, tenant: Any, **kwargs: Any) -> ReturnDiscrepancy:
        return ReturnDiscrepancy.objects.create(tenant=tenant, **kwargs)


class SupplierCreditNoteRepository:
    """Repository encapsulating persistence operations for SupplierCreditNote."""

    def create(self, tenant: Any, **kwargs: Any) -> SupplierCreditNote:
        return SupplierCreditNote.objects.create(tenant=tenant, **kwargs)

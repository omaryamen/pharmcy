"""Repository layer for PurchaseOrder persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.procurement.models import PurchaseOrder, PurchaseOrderAmendment, PurchaseOrderLine


class PurchaseOrderRepository:
    """Repository encapsulating persistence operations for PurchaseOrder."""

    def get_queryset(self, tenant: Any) -> QuerySet[PurchaseOrder]:
        return PurchaseOrder.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, po_id: str) -> PurchaseOrder | None:
        return self.get_queryset(tenant).filter(pk=po_id).first()

    def find_by_number(self, tenant: Any, number: str) -> PurchaseOrder | None:
        return self.get_queryset(tenant).filter(po_number=number).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> PurchaseOrder | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseOrder:
        return PurchaseOrder.objects.create(tenant=tenant, **kwargs)

    def update(self, po: PurchaseOrder, **kwargs: Any) -> PurchaseOrder:
        for field, value in kwargs.items():
            setattr(po, field, value)
        po.save()
        return po


class PurchaseOrderLineRepository:
    """Repository encapsulating persistence operations for PurchaseOrderLine."""

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseOrderLine:
        return PurchaseOrderLine.objects.create(tenant=tenant, **kwargs)


class PurchaseOrderAmendmentRepository:
    """Repository encapsulating persistence operations for PurchaseOrderAmendment."""

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseOrderAmendment:
        return PurchaseOrderAmendment.objects.create(tenant=tenant, **kwargs)

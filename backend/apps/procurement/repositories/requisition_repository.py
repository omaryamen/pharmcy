"""Repository layer for PurchaseRequisition persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.procurement.models import PurchaseRequisition, PurchaseRequisitionLine


class PurchaseRequisitionRepository:
    """Repository encapsulating persistence operations for PurchaseRequisition."""

    def get_queryset(self, tenant: Any) -> QuerySet[PurchaseRequisition]:
        return PurchaseRequisition.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, requisition_id: str) -> PurchaseRequisition | None:
        return self.get_queryset(tenant).filter(pk=requisition_id).first()

    def find_by_number(self, tenant: Any, number: str) -> PurchaseRequisition | None:
        return self.get_queryset(tenant).filter(requisition_number=number).first()

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseRequisition:
        return PurchaseRequisition.objects.create(tenant=tenant, **kwargs)

    def update(self, requisition: PurchaseRequisition, **kwargs: Any) -> PurchaseRequisition:
        for field, value in kwargs.items():
            setattr(requisition, field, value)
        requisition.save()
        return requisition


class PurchaseRequisitionLineRepository:
    """Repository encapsulating persistence operations for PurchaseRequisitionLine."""

    def create(self, tenant: Any, **kwargs: Any) -> PurchaseRequisitionLine:
        return PurchaseRequisitionLine.objects.create(tenant=tenant, **kwargs)

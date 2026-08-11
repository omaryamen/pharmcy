"""Query selector layer for PurchaseRequisition reporting and search."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.procurement.models import PurchaseRequisition


class PurchaseRequisitionSelector:
    """Selector providing optimized query methods for PurchaseRequisition."""

    def list_requisitions(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        search: str | None = None,
    ) -> QuerySet[PurchaseRequisition]:
        qs = (
            PurchaseRequisition.objects.filter(tenant=tenant)
            .select_related("company", "branch", "warehouse", "requested_by", "approved_by", "rejected_by")
            .prefetch_related("lines__medicine", "lines__preferred_supplier")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(requisition_number__icontains=search) | qs.filter(department__icontains=search)

        return qs

    def get_requisition_by_id(self, tenant: Any, requisition_id: str) -> PurchaseRequisition | None:
        return (
            PurchaseRequisition.objects.filter(tenant=tenant, pk=requisition_id)
            .select_related("company", "branch", "warehouse", "requested_by", "approved_by", "rejected_by")
            .prefetch_related("lines__medicine", "lines__preferred_supplier")
            .first()
        )

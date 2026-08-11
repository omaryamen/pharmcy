"""Query selector layer for PurchaseOrder reporting, search, and analytics."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.procurement.models import PurchaseOrder


class PurchaseOrderSelector:
    """Selector providing query methods and analytics for PurchaseOrder."""

    def list_purchase_orders(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        supplier_id: str | None = None,
        medicine_id: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        order_date_start: Any | None = None,
        order_date_end: Any | None = None,
        search: str | None = None,
    ) -> QuerySet[PurchaseOrder]:
        qs = (
            PurchaseOrder.objects.filter(tenant=tenant)
            .select_related("company", "branch", "supplier", "warehouse", "created_by", "approved_by", "cancelled_by")
            .prefetch_related("lines__medicine", "amendments")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if medicine_id:
            qs = qs.filter(lines__medicine_id=medicine_id).distinct()
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if order_date_start:
            qs = qs.filter(order_date__gte=order_date_start)
        if order_date_end:
            qs = qs.filter(order_date__lte=order_date_end)
        if search:
            qs = qs.filter(
                Q(po_number__icontains=search)
                | Q(supplier_reference__icontains=search)
                | Q(supplier__legal_name__icontains=search)
            )

        return qs

    def get_purchase_order_by_id(self, tenant: Any, po_id: str) -> PurchaseOrder | None:
        return (
            PurchaseOrder.objects.filter(tenant=tenant, pk=po_id)
            .select_related("company", "branch", "supplier", "warehouse", "requisition", "created_by", "approved_by", "cancelled_by")
            .prefetch_related("lines__medicine", "lines__storage_location", "amendments")
            .first()
        )

    def get_procurement_statistics(self, tenant: Any, company_id: str | None = None) -> dict[str, Any]:
        qs = PurchaseOrder.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)

        today = timezone.now().date()

        total_pos = qs.count()
        total_spend = qs.exclude(status="cancelled").aggregate(total=Sum("grand_total"))["total"] or 0

        pending_approval = qs.filter(status="pending_approval").count()
        sent_to_supplier = qs.filter(status="sent_to_supplier").count()
        open_orders = qs.filter(status__in=["approved", "sent_to_supplier", "acknowledged", "partially_received"]).count()
        overdue_deliveries = qs.filter(status__in=["sent_to_supplier", "acknowledged", "partially_received"], expected_delivery_date__lt=today).count()

        status_breakdown = dict(qs.values_list("status").annotate(count=Count("id")))

        return {
            "total_purchase_orders": total_pos,
            "total_procurement_spend": str(total_spend),
            "pending_approval_count": pending_approval,
            "sent_to_supplier_count": sent_to_supplier,
            "open_orders_count": open_orders,
            "overdue_deliveries_count": overdue_deliveries,
            "status_breakdown": status_breakdown,
        }

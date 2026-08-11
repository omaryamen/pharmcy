"""Query selector layer for PurchaseReturn search and analytics."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet, Sum

from apps.purchase_returns.models import PurchaseReturn


class PurchaseReturnSelector:
    """Selector providing query methods and analytics for PurchaseReturn."""

    def list_purchase_returns(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        supplier_id: str | None = None,
        goods_receipt_id: str | None = None,
        purchase_order_id: str | None = None,
        medicine_id: str | None = None,
        batch_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[PurchaseReturn]:
        qs = (
            PurchaseReturn.objects.filter(tenant=tenant)
            .select_related("company", "branch", "supplier", "purchase_order", "goods_receipt", "warehouse", "requested_by", "approved_by", "dispatched_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location", "discrepancies", "credit_notes")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if goods_receipt_id:
            qs = qs.filter(goods_receipt_id=goods_receipt_id)
        if purchase_order_id:
            qs = qs.filter(purchase_order_id=purchase_order_id)
        if medicine_id:
            qs = qs.filter(lines__medicine_id=medicine_id).distinct()
        if batch_id:
            qs = qs.filter(lines__batch_id=batch_id).distinct()
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(return_number__icontains=search)
                | Q(supplier__legal_name__icontains=search)
            )

        return qs

    def get_purchase_return_by_id(self, tenant: Any, return_id: str) -> PurchaseReturn | None:
        return (
            PurchaseReturn.objects.filter(tenant=tenant, pk=return_id)
            .select_related("company", "branch", "supplier", "purchase_order", "goods_receipt", "warehouse", "requested_by", "approved_by", "dispatched_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location", "discrepancies", "credit_notes")
            .first()
        )

    def get_return_statistics(self, tenant: Any, company_id: str | None = None) -> dict[str, Any]:
        qs = PurchaseReturn.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)

        total_returns = qs.count()
        total_returned_value = qs.filter(status="accepted").aggregate(total=Sum("grand_total"))["total"] or 0

        pending_approval = qs.filter(status="pending_approval").count()
        dispatched_returns = qs.filter(status="dispatched").count()
        discrepancies_count = qs.filter(status="discrepancy").count()

        status_breakdown = dict(qs.values_list("status").annotate(count=Count("id")))

        return {
            "total_purchase_returns": total_returns,
            "total_returned_value": str(total_returned_value),
            "pending_approval_count": pending_approval,
            "dispatched_returns_count": dispatched_returns,
            "discrepancies_count": discrepancies_count,
            "status_breakdown": status_breakdown,
        }

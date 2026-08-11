"""Query selector layer for GoodsReceipt search and analytics."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet, Sum

from apps.goods_receipt.models import GoodsReceipt


class GoodsReceiptSelector:
    """Selector providing query methods and analytics for GoodsReceipt."""

    def list_goods_receipts(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        supplier_id: str | None = None,
        purchase_order_id: str | None = None,
        medicine_id: str | None = None,
        batch_number: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[GoodsReceipt]:
        qs = (
            GoodsReceipt.objects.filter(tenant=tenant)
            .select_related("company", "branch", "supplier", "purchase_order", "warehouse", "receiving_location", "received_by", "verified_by", "approved_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if purchase_order_id:
            qs = qs.filter(purchase_order_id=purchase_order_id)
        if medicine_id:
            qs = qs.filter(lines__medicine_id=medicine_id).distinct()
        if batch_number:
            qs = qs.filter(lines__batch_number__icontains=batch_number).distinct()
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(receipt_number__icontains=search)
                | Q(supplier_delivery_number__icontains=search)
                | Q(supplier_invoice_reference__icontains=search)
                | Q(supplier__legal_name__icontains=search)
            )

        return qs

    def get_goods_receipt_by_id(self, tenant: Any, receipt_id: str) -> GoodsReceipt | None:
        return (
            GoodsReceipt.objects.filter(tenant=tenant, pk=receipt_id)
            .select_related("company", "branch", "supplier", "purchase_order", "warehouse", "receiving_location", "received_by", "verified_by", "approved_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location")
            .first()
        )

    def get_receiving_statistics(self, tenant: Any, company_id: str | None = None) -> dict[str, Any]:
        qs = GoodsReceipt.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)

        total_receipts = qs.count()
        total_received_value = qs.filter(status="completed").aggregate(total=Sum("grand_total"))["total"] or 0

        pending_verification = qs.filter(status="pending_verification").count()
        completed_receipts = qs.filter(status="completed").count()

        status_breakdown = dict(qs.values_list("status").annotate(count=Count("id")))

        return {
            "total_goods_receipts": total_receipts,
            "total_received_value": str(total_received_value),
            "pending_verification_count": pending_verification,
            "completed_receipts_count": completed_receipts,
            "status_breakdown": status_breakdown,
        }

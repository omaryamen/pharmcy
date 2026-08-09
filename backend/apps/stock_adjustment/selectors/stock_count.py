"""Selector queries for Stock Count and variance reporting data."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from apps.stock_adjustment.models import StockCount, StockCountHistory, StockCountLine


class StockCountSelector:
    """Selector queries for retrieving stock count documents, line items, and reporting statistics."""

    def list_counts(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        count_type: str | None = None,
        count_status: str | None = None,
        created_by_id: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
    ):
        qs = (
            StockCount.objects.filter(tenant=tenant)
            .select_related("company", "branch", "warehouse", "storage_location", "created_by", "approved_by")
            .prefetch_related("lines")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if count_type:
            qs = qs.filter(count_type=count_type)
        if count_status:
            qs = qs.filter(count_status=count_status)
        if created_by_id:
            qs = qs.filter(created_by_id=created_by_id)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        if search:
            qs = qs.filter(
                Q(count_number__icontains=search)
                | Q(reason__icontains=search)
                | Q(notes__icontains=search)
                | Q(warehouse__name__icontains=search)
            )

        return qs.order_by("-created_at")

    def get_count_by_id(self, tenant: Any, count_id: str) -> StockCount | None:
        return (
            StockCount.objects.filter(tenant=tenant, pk=count_id)
            .select_related("company", "branch", "warehouse", "storage_location", "created_by", "started_by", "approved_by", "reconciled_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location", "sessions", "history")
            .first()
        )

    def get_count_variance_summary(self, tenant: Any, count_id: str) -> dict[str, Any]:
        count = self.get_count_by_id(tenant, count_id)
        if not count:
            return {}

        lines = count.lines.all()
        total_items = lines.count()
        counted_items = lines.filter(counted_quantity__isnull=False).count()

        shortage_lines = lines.filter(variance_quantity__lt=Decimal("0.00"))
        overage_lines = lines.filter(variance_quantity__gt=Decimal("0.00"))
        exact_lines = lines.filter(variance_quantity=Decimal("0.00"), counted_quantity__isnull=False)

        total_shortage_qty = shortage_lines.aggregate(s=Sum("variance_quantity"))["s"] or Decimal("0.00")
        total_overage_qty = overage_lines.aggregate(s=Sum("variance_quantity"))["s"] or Decimal("0.00")
        total_variance_cost = lines.aggregate(s=Sum("variance_cost"))["s"] or Decimal("0.0000")

        return {
            "count_number": count.count_number,
            "count_status": count.count_status,
            "total_items": total_items,
            "counted_items": counted_items,
            "shortage_item_count": shortage_lines.count(),
            "overage_item_count": overage_lines.count(),
            "exact_match_count": exact_lines.count(),
            "total_shortage_quantity": abs(total_shortage_qty),
            "total_overage_quantity": total_overage_qty,
            "net_variance_quantity": total_overage_qty + total_shortage_qty,
            "total_variance_cost": total_variance_cost,
        }

    def get_count_history(self, tenant: Any, count_id: str):
        return (
            StockCountHistory.objects.filter(tenant=tenant, stock_count_id=count_id)
            .select_related("performed_by")
            .order_by("timestamp")
        )

    def get_reporting_summary(self, tenant: Any, *, company_id: str | None = None, warehouse_id: str | None = None) -> dict[str, Any]:
        qs = StockCountLine.objects.filter(tenant=tenant, stock_count__count_status="reconciled")
        if company_id:
            qs = qs.filter(stock_count__company_id=company_id)
        if warehouse_id:
            qs = qs.filter(stock_count__warehouse_id=warehouse_id)

        agg = qs.aggregate(
            total_variance_cost=Sum("variance_cost"),
            total_shortage_qty=Sum("variance_quantity", filter=Q(variance_quantity__lt=0)),
            total_overage_qty=Sum("variance_quantity", filter=Q(variance_quantity__gt=0)),
        )

        return {
            "total_reconciled_lines": qs.count(),
            "total_variance_cost": agg["total_variance_cost"] or Decimal("0.0000"),
            "total_shortage_quantity": abs(agg["total_shortage_qty"] or Decimal("0.00")),
            "total_overage_quantity": agg["total_overage_qty"] or Decimal("0.00"),
        }

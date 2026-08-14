"""SalesReportSelector consuming operational SalesInvoice data for sales performance analytics."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate

from apps.reports.selectors.dto import ReportFilterDTO
from apps.sales.models import SalesInvoice, SalesInvoiceLine, SalesStatus


class SalesReportSelector:
    """Selector compiling sales reports and POS performance breakdowns."""

    def _base_queryset(self, filters: ReportFilterDTO):
        start_date, end_date = filters.resolve_dates()
        qs = SalesInvoice.objects.filter(
            tenant=filters.tenant,
            status=SalesStatus.COMPLETED,
            invoice_date__gte=start_date,
            invoice_date__lte=end_date,
        )
        if filters.company_id:
            qs = qs.filter(company_id=filters.company_id)
        if filters.branch_id:
            qs = qs.filter(branch_id=filters.branch_id)
        if filters.customer_id:
            qs = qs.filter(customer_id=filters.customer_id)
        if filters.user_id:
            qs = qs.filter(cashier_id=filters.user_id)
        return qs

    def get_sales_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Aggregate total gross sales, discounts, net sales, tax, invoice count, and average invoice value."""
        qs = self._base_queryset(filters)
        agg = qs.aggregate(
            gross=Sum("subtotal"),
            discounts=Sum("discount"),
            tax=Sum("tax"),
            net=Sum("grand_total"),
            inv_count=Count("id"),
        )

        gross = agg["gross"] or Decimal("0.0000")
        discounts = agg["discounts"] or Decimal("0.0000")
        tax = agg["tax"] or Decimal("0.0000")
        net = agg["net"] or Decimal("0.0000")
        inv_count = agg["inv_count"] or 0
        avg_value = net / inv_count if inv_count > 0 else Decimal("0.0000")

        return {
            "gross_sales": gross,
            "total_discounts": discounts,
            "total_tax": tax,
            "net_sales": net,
            "invoice_count": inv_count,
            "average_transaction_value": avg_value,
        }

    def get_sales_by_branch(self, filters: ReportFilterDTO) -> list[dict[str, Any]]:
        """Sales totals aggregated by branch."""
        qs = self._base_queryset(filters)
        grouped = (
            qs.values("branch__id", "branch__name", "branch__code")
            .annotate(
                net_sales=Sum("grand_total"),
                invoice_count=Count("id"),
            )
            .order_by("-net_sales")
        )
        return [
            {
                "branch_id": str(item["branch__id"]),
                "branch_name": item["branch__name"] or "Unassigned",
                "branch_code": item["branch__code"] or "",
                "net_sales": item["net_sales"] or Decimal("0.0000"),
                "invoice_count": item["invoice_count"],
            }
            for item in grouped
        ]

    def get_sales_by_cashier(self, filters: ReportFilterDTO) -> list[dict[str, Any]]:
        """Sales totals aggregated by cashier user."""
        qs = self._base_queryset(filters)
        grouped = (
            qs.values("cashier__id", "cashier__first_name", "cashier__last_name", "cashier__email")
            .annotate(
                net_sales=Sum("grand_total"),
                invoice_count=Count("id"),
            )
            .order_by("-net_sales")
        )
        return [
            {
                "cashier_id": str(item["cashier__id"]),
                "cashier_name": f"{item['cashier__first_name']} {item['cashier__last_name']}".strip() or item["cashier__email"],
                "net_sales": item["net_sales"] or Decimal("0.0000"),
                "invoice_count": item["invoice_count"],
            }
            for item in grouped
        ]

    def get_sales_trend(self, filters: ReportFilterDTO) -> list[dict[str, Any]]:
        """Daily sales trend over the resolved date range."""
        qs = self._base_queryset(filters)
        trend = (
            qs.annotate(day=TruncDate("invoice_date"))
            .values("day")
            .annotate(net_sales=Sum("grand_total"), invoice_count=Count("id"))
            .order_by("day")
        )
        return [
            {
                "date": item["day"].strftime("%Y-%m-%d"),
                "net_sales": item["net_sales"] or Decimal("0.0000"),
                "invoice_count": item["invoice_count"],
            }
            for item in trend
        ]

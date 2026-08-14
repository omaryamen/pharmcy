"""PurchasingReportSelector compiling purchase order analysis and supplier AP aging reports."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Sum

from apps.accounts_payable.selectors import AccountsPayableSelector
from apps.procurement.models import PurchaseOrder
from apps.reports.selectors.dto import ReportFilterDTO


class PurchasingReportSelector:
    """Selector compiling purchasing analytics and supplier AP financial reports."""

    def __init__(self, ap_selector: AccountsPayableSelector | None = None) -> None:
        self.ap_selector = ap_selector or AccountsPayableSelector()

    def get_purchasing_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Aggregate total purchase orders and total committed purchase amount."""
        start_date, end_date = filters.resolve_dates()
        qs = PurchaseOrder.objects.filter(
            tenant=filters.tenant,
            order_date__gte=start_date,
            order_date__lte=end_date,
        )
        if filters.company_id:
            qs = qs.filter(company_id=filters.company_id)
        if filters.branch_id:
            qs = qs.filter(branch_id=filters.branch_id)

        agg = qs.aggregate(
            total_val=Sum("total_amount"),
            po_count=Count("id"),
        )
        return {
            "total_purchase_orders_count": agg["po_count"] or 0,
            "total_purchase_value": agg["total_val"] or Decimal("0.0000"),
        }

    def get_supplier_ap_aging(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Delegates to authoritative AccountsPayableSelector for supplier AP aging."""
        return self.ap_selector.get_ap_aging_summary(
            tenant=filters.tenant,
            company_id=filters.company_id,
            supplier_id=filters.supplier_id,
        )

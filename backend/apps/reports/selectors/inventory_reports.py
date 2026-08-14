"""InventoryReportSelector compiling stock valuation, expired stock, low stock, and stock ledger movements."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import F, Q, Sum
from django.utils import timezone

from apps.alerts.models import InventoryAlert
from apps.inventory.models import InventoryItem
from apps.reports.selectors.dto import ReportFilterDTO
from apps.stock_movement.models import StockMovement


class InventoryReportSelector:
    """Selector providing stock valuation, expiry, low stock, and inventory movement ledger reports."""

    def get_stock_valuation_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Calculate total inventory quantity and total valuation across warehouses/branches."""
        qs = InventoryItem.objects.filter(tenant=filters.tenant).select_related("batch", "warehouse", "medicine")
        if filters.company_id:
            qs = qs.filter(warehouse__company_id=filters.company_id)
        if filters.branch_id:
            qs = qs.filter(warehouse__branch_id=filters.branch_id)
        if filters.warehouse_id:
            qs = qs.filter(warehouse_id=filters.warehouse_id)

        items = list(qs)
        total_qty = sum((item.quantity_on_hand for item in items), Decimal("0.0000"))
        total_value = sum((item.quantity_on_hand * item.average_cost for item in items), Decimal("0.0000"))

        return {
            "total_inventory_items_count": len(items),
            "total_quantity_on_hand": total_qty,
            "total_inventory_valuation": total_value,
        }

    def get_low_stock_items(self, filters: ReportFilterDTO) -> list[dict[str, Any]]:
        """List active inventory alerts for low stock or out of stock items."""
        qs = InventoryAlert.objects.filter(tenant=filters.tenant, is_resolved=False, alert_type__in=["low_stock", "out_of_stock"]).select_related("medicine", "warehouse")
        if filters.branch_id:
            qs = qs.filter(warehouse__branch_id=filters.branch_id)
        if filters.warehouse_id:
            qs = qs.filter(warehouse_id=filters.warehouse_id)

        return [
            {
                "alert_id": str(alert.pk),
                "medicine_name": alert.medicine.trade_name or alert.medicine.english_name,
                "warehouse_name": alert.warehouse.name if alert.warehouse else "",
                "alert_type": alert.alert_type,
                "current_quantity": alert.current_quantity,
                "reorder_level": alert.reorder_level,
            }
            for alert in qs[:100]
        ]

    def get_expiry_risk_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Aggregate expired and near-expiry batch counts and total monetary loss risk."""
        today = timezone.now().date()
        cutoff_30 = today + timezone.timedelta(days=30)

        qs = InventoryItem.objects.filter(tenant=filters.tenant, quantity_on_hand__gt=Decimal("0.0000")).select_related("batch")
        if filters.branch_id:
            qs = qs.filter(warehouse__branch_id=filters.branch_id)

        expired_items = [i for i in qs if i.batch.expiry_date and i.batch.expiry_date < today]
        near_expiry_items = [i for i in qs if i.batch.expiry_date and today <= i.batch.expiry_date <= cutoff_30]

        expired_val = sum((i.quantity_on_hand * i.unit_cost for i in expired_items), Decimal("0.0000"))
        near_expiry_val = sum((i.quantity_on_hand * i.unit_cost for i in near_expiry_items), Decimal("0.0000"))

        return {
            "expired_batches_count": len(expired_items),
            "expired_stock_value": expired_val,
            "near_expiry_30_days_count": len(near_expiry_items),
            "near_expiry_stock_value": near_expiry_val,
        }

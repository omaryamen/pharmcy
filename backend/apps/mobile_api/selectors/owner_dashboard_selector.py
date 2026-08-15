"""PharmacyOwnerMobileSelector aggregating business health indicators for pharmacy owners and managers."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.db.models import Sum
from django.utils import timezone

from apps.alerts.models import AlertSeverity, AlertStatus, AlertType, InventoryAlert
from apps.branches.models import Branch
from apps.core.models import Tenant
from apps.inventory.models import InventoryItem
from apps.sales.models import SalesInvoice, SalesStatus


class PharmacyOwnerMobileSelector:
    """Selector calculating real-time executive summaries for Pharmacy Owner Mobile App."""

    def get_owner_dashboard(self, tenant: Tenant) -> dict[str, Any]:
        """Aggregate today's sales, active inventory stock count, low-stock alerts, and branch metrics."""
        today = timezone.now().date()

        # 1. Today's POS & Online Sales
        today_sales_total = (
            SalesInvoice.objects.filter(
                tenant=tenant,
                status=SalesStatus.COMPLETED,
                invoice_date=today,
            ).aggregate(total=Sum("grand_total"))["total"]
            or Decimal("0.00")
        )

        # 2. Total Inventory Balance & Low Stock Alerts
        total_stock_items = (
            InventoryItem.objects.filter(tenant=tenant, is_deleted=False).aggregate(total=Sum("on_hand_quantity"))["total"]
            or Decimal("0.00")
        )

        low_stock_alerts_count = InventoryAlert.objects.filter(
            tenant=tenant,
            alert_type__in=[AlertType.LOW_STOCK, AlertType.OUT_OF_STOCK],
            status=AlertStatus.ACTIVE,
        ).count()

        near_expiry_alerts_count = InventoryAlert.objects.filter(
            tenant=tenant,
            alert_type__in=[AlertType.EXPIRY_WARNING, AlertType.EXPIRED],
            status=AlertStatus.ACTIVE,
        ).count()

        # 3. Branches count
        active_branches_count = Branch.objects.filter(tenant=tenant, is_deleted=False).count()

        return {
            "tenant_id": str(tenant.pk),
            "today_sales": float(today_sales_total),
            "total_stock_units": float(total_stock_items),
            "low_stock_alerts_count": low_stock_alerts_count,
            "near_expiry_alerts_count": near_expiry_alerts_count,
            "active_branches_count": active_branches_count,
        }

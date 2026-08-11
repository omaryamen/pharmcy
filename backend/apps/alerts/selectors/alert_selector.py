"""Query selector layer for InventoryAlert reporting and search."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, QuerySet

from apps.alerts.models import InventoryAlert


class InventoryAlertSelector:
    """Selector providing optimized query methods for InventoryAlert."""

    def list_alerts(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        warehouse_id: str | None = None,
        medicine_id: str | None = None,
        alert_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[InventoryAlert]:
        qs = (
            InventoryAlert.objects.filter(tenant=tenant)
            .select_related("company", "warehouse", "storage_location", "medicine", "batch", "acknowledged_by", "resolved_by")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if alert_type:
            qs = qs.filter(alert_type=alert_type)
        if severity:
            qs = qs.filter(severity=severity)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(alert_number__icontains=search)

        return qs

    def get_alert_by_id(self, tenant: Any, alert_id: str) -> InventoryAlert | None:
        return (
            InventoryAlert.objects.filter(tenant=tenant, pk=alert_id)
            .select_related("company", "warehouse", "storage_location", "medicine", "batch", "acknowledged_by", "resolved_by")
            .first()
        )

    def get_alert_statistics(self, tenant: Any, company_id: str | None = None) -> dict[str, Any]:
        qs = InventoryAlert.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)

        active_qs = qs.filter(status__in=["active", "acknowledged"])

        total_active = active_qs.count()
        critical_count = active_qs.filter(severity="critical").count()
        high_count = active_qs.filter(severity="high").count()
        medium_count = active_qs.filter(severity="medium").count()
        low_count = active_qs.filter(severity="low").count()

        type_breakdown = dict(active_qs.values_list("alert_type").annotate(count=Count("id")))

        return {
            "total_active_alerts": total_active,
            "critical_alerts": critical_count,
            "high_alerts": high_count,
            "medium_alerts": medium_count,
            "low_alerts": low_count,
            "type_breakdown": type_breakdown,
        }

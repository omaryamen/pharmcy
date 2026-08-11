"""Repository layer for InventoryAlert persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.alerts.models import InventoryAlert


class InventoryAlertRepository:
    """Repository encapsulating persistence operations for InventoryAlert."""

    def get_queryset(self, tenant: Any) -> QuerySet[InventoryAlert]:
        return InventoryAlert.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, alert_id: str) -> InventoryAlert | None:
        return self.get_queryset(tenant).filter(pk=alert_id).first()

    def find_active_alert(
        self, tenant: Any, alert_type: str, medicine: Any, batch: Any | None = None, warehouse: Any | None = None
    ) -> InventoryAlert | None:
        qs = self.get_queryset(tenant).filter(
            alert_type=alert_type,
            medicine=medicine,
            status__in=["active", "acknowledged"],
        )
        if batch:
            qs = qs.filter(batch=batch)
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        return qs.first()

    def create(self, tenant: Any, **kwargs: Any) -> InventoryAlert:
        return InventoryAlert.objects.create(tenant=tenant, **kwargs)

    def update(self, alert: InventoryAlert, **kwargs: Any) -> InventoryAlert:
        for field, value in kwargs.items():
            setattr(alert, field, value)
        alert.save()
        return alert

"""Collision-safe sequence code generator for alerts and recalls."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.alerts.models import BatchRecall, InventoryAlert


class AlertNumberGenerator:
    """Generates sequential document codes for alerts (ALT-YYYY-XXXXXX) and recalls (RCL-YYYY-XXXXXX)."""

    @transaction.atomic
    def generate_alert_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"ALT-{year}-"

        last_alert = (
            InventoryAlert.objects.filter(tenant=tenant, alert_number__startswith=prefix)
            .order_by("-alert_number")
            .select_for_update()
            .first()
        )

        if not last_alert:
            seq = 1
        else:
            try:
                seq = int(last_alert.alert_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_recall_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"RCL-{year}-"

        last_recall = (
            BatchRecall.objects.filter(tenant=tenant, recall_number__startswith=prefix)
            .order_by("-recall_number")
            .select_for_update()
            .first()
        )

        if not last_recall:
            seq = 1
        else:
            try:
                seq = int(last_recall.recall_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

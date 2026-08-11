"""Authoritative Alert Scanner Service evaluating stock balances and batch expiry."""

from __future__ import annotations

import logging
from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.alerts.models import AlertSeverity, AlertStatus, AlertType, InventoryAlert
from apps.alerts.repositories import InventoryAlertRepository
from apps.alerts.services.number_generator import AlertNumberGenerator
from apps.alerts.validators import validate_alert_can_be_acknowledged, validate_alert_can_be_resolved
from apps.inventory.models import Batch, InventoryItem

logger = logging.getLogger(__name__)


class AlertScannerService:
    """Evaluates inventory balances and pharmaceutical batch expiry dates, generating/updating InventoryAlert records."""

    def __init__(self):
        self.alert_repository = InventoryAlertRepository()
        self.number_generator = AlertNumberGenerator()

    @transaction.atomic
    def scan_inventory_alerts(
        self,
        tenant: Any,
        company: Any | None = None,
        warehouse: Any | None = None,
        near_expiry_days: int = 90,
        critical_expiry_days: int = 30,
        user: Any | None = None,
    ) -> dict[str, int]:
        """Scan active inventory items and batches to create/update inventory alerts."""
        now = timezone.now()
        today = now.date()

        alerts_created = 0
        alerts_updated = 0

        # Query active inventory items
        inv_qs = InventoryItem.objects.filter(tenant=tenant)
        if company:
            inv_qs = inv_qs.filter(company=company)
        if warehouse:
            inv_qs = inv_qs.filter(warehouse=warehouse)

        inv_qs = inv_qs.select_related("company", "warehouse", "storage_location", "medicine", "batch")

        for item in inv_qs:
            # 1. Out of Stock Check
            if item.on_hand_quantity <= Decimal("0"):
                created = self._trigger_or_update_alert(
                    tenant=tenant,
                    company=item.company,
                    warehouse=item.warehouse,
                    storage_location=item.storage_location,
                    medicine=item.medicine,
                    batch=item.batch,
                    alert_type=AlertType.OUT_OF_STOCK,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Out of Stock: {item.medicine.english_name}",
                    message=f"Medicine {item.medicine.english_name} (SKU: {item.medicine.sku}) has zero on-hand quantity at warehouse {item.warehouse.name}.",
                    current_val=item.on_hand_quantity,
                    threshold_val=Decimal("0.0000"),
                    now=now,
                )
                if created:
                    alerts_created += 1
                else:
                    alerts_updated += 1
            # 2. Low Stock / Reorder Point Check
            elif item.reorder_point and item.on_hand_quantity <= item.reorder_point:
                created = self._trigger_or_update_alert(
                    tenant=tenant,
                    company=item.company,
                    warehouse=item.warehouse,
                    storage_location=item.storage_location,
                    medicine=item.medicine,
                    batch=item.batch,
                    alert_type=AlertType.LOW_STOCK,
                    severity=AlertSeverity.HIGH if item.on_hand_quantity <= (item.reorder_point / 2) else AlertSeverity.MEDIUM,
                    title=f"Low Stock Warning: {item.medicine.english_name}",
                    message=f"Medicine {item.medicine.english_name} on-hand stock ({item.on_hand_quantity}) is at or below reorder point ({item.reorder_point}).",
                    current_val=item.on_hand_quantity,
                    threshold_val=item.reorder_point,
                    now=now,
                )
                if created:
                    alerts_created += 1
                else:
                    alerts_updated += 1

        # Query active batches for Expiry Scans
        batch_qs = Batch.objects.filter(tenant=tenant, status="active")
        if company:
            batch_qs = batch_qs.filter(company=company)

        batch_qs = batch_qs.select_related("company", "medicine")

        near_expiry_cutoff = today + timedelta(days=near_expiry_days)
        critical_expiry_cutoff = today + timedelta(days=critical_expiry_days)

        for batch in batch_qs:
            if not batch.expiry_date:
                continue

            days_to_expiry = (batch.expiry_date - today).days

            # 1. Expired Check
            if batch.expiry_date <= today:
                # Find inventory positions for this batch
                items = InventoryItem.objects.filter(tenant=tenant, batch=batch, on_hand_quantity__gt=Decimal("0")).select_related("warehouse", "storage_location")
                for item in items:
                    created = self._trigger_or_update_alert(
                        tenant=tenant,
                        company=batch.company,
                        warehouse=item.warehouse,
                        storage_location=item.storage_location,
                        medicine=batch.medicine,
                        batch=batch,
                        alert_type=AlertType.EXPIRED,
                        severity=AlertSeverity.CRITICAL,
                        title=f"Expired Batch: {batch.batch_number} - {batch.medicine.english_name}",
                        message=f"Batch {batch.batch_number} for medicine {batch.medicine.english_name} expired on {batch.expiry_date}. Current on-hand quantity: {item.on_hand_quantity}.",
                        current_val=item.on_hand_quantity,
                        threshold_val=Decimal("0.0000"),
                        now=now,
                    )
                    if created:
                        alerts_created += 1
                    else:
                        alerts_updated += 1

            # 2. Near / Critical Expiry Warning
            elif batch.expiry_date <= near_expiry_cutoff:
                is_critical = batch.expiry_date <= critical_expiry_cutoff
                sev = AlertSeverity.HIGH if is_critical else AlertSeverity.MEDIUM

                items = InventoryItem.objects.filter(tenant=tenant, batch=batch, on_hand_quantity__gt=Decimal("0")).select_related("warehouse", "storage_location")
                for item in items:
                    created = self._trigger_or_update_alert(
                        tenant=tenant,
                        company=batch.company,
                        warehouse=item.warehouse,
                        storage_location=item.storage_location,
                        medicine=batch.medicine,
                        batch=batch,
                        alert_type=AlertType.EXPIRY_WARNING,
                        severity=sev,
                        title=f"Expiring Batch ({days_to_expiry} days): {batch.batch_number}",
                        message=f"Batch {batch.batch_number} for medicine {batch.medicine.english_name} will expire in {days_to_expiry} days ({batch.expiry_date}). On-hand quantity: {item.on_hand_quantity}.",
                        current_val=item.on_hand_quantity,
                        threshold_val=Decimal(str(days_to_expiry)),
                        now=now,
                    )
                    if created:
                        alerts_created += 1
                    else:
                        alerts_updated += 1

        logger.info("Scanned inventory alerts for tenant %s: created=%d, updated=%d", tenant, alerts_created, alerts_updated)
        return {"alerts_created": alerts_created, "alerts_updated": alerts_updated}

    def _trigger_or_update_alert(
        self,
        tenant: Any,
        company: Any,
        warehouse: Any | None,
        storage_location: Any | None,
        medicine: Any,
        batch: Any | None,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        current_val: Decimal,
        threshold_val: Decimal,
        now: Any,
    ) -> bool:
        """Internal helper to create a new alert or update existing active alert."""
        existing = self.alert_repository.find_active_alert(
            tenant=tenant, alert_type=alert_type, medicine=medicine, batch=batch, warehouse=warehouse
        )

        if existing:
            existing.current_value = current_val
            existing.threshold_value = threshold_val
            existing.severity = severity
            existing.message = message
            existing.save(update_fields=["current_value", "threshold_value", "severity", "message", "updated_at"])
            return False

        alt_num = self.number_generator.generate_alert_number(tenant)
        self.alert_repository.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            storage_location=storage_location,
            medicine=medicine,
            batch=batch,
            alert_number=alt_num,
            alert_type=alert_type,
            severity=severity,
            status=AlertStatus.ACTIVE,
            title=title,
            message=message,
            current_value=current_val,
            threshold_value=threshold_val,
            triggered_at=now,
        )
        return True

    @transaction.atomic
    def acknowledge_alert(self, tenant: Any, alert: InventoryAlert, user: Any | None = None) -> InventoryAlert:
        """Acknowledge an active alert."""
        validate_alert_can_be_acknowledged(alert)
        now = timezone.now()
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = now
        alert.acknowledged_by = user
        alert.save(update_fields=["status", "acknowledged_at", "acknowledged_by", "updated_at"])
        logger.info("Acknowledged alert %s", alert.alert_number)
        return alert

    @transaction.atomic
    def resolve_alert(self, tenant: Any, alert: InventoryAlert, resolution_notes: str = "", user: Any | None = None) -> InventoryAlert:
        """Resolve an active or acknowledged alert."""
        validate_alert_can_be_resolved(alert)
        now = timezone.now()
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = now
        alert.resolved_by = user
        alert.resolution_notes = resolution_notes
        alert.save(update_fields=["status", "resolved_at", "resolved_by", "resolution_notes", "updated_at"])
        logger.info("Resolved alert %s", alert.alert_number)
        return alert

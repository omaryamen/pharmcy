"""Inventory Alert entity tracking stock warnings, expiry notices, and compliance alerts."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.alerts.models.enums import AlertSeverity, AlertStatus, AlertType
from apps.common.models import FullAuditModel, TenantAwareModel


class InventoryAlert(TenantAwareModel, FullAuditModel):
    """Real-time inventory alert record for low stock, expiry, recalls, and temperature excursions."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="inventory_alerts",
        verbose_name=_("Company"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.SET_NULL,
        related_name="inventory_alerts",
        null=True,
        blank=True,
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="inventory_alerts",
        null=True,
        blank=True,
        verbose_name=_("Storage Location"),
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="inventory_alerts",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        related_name="inventory_alerts",
        null=True,
        blank=True,
        verbose_name=_("Batch"),
        db_index=True,
    )

    alert_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Alert Number"))

    alert_type = models.CharField(
        max_length=40,
        choices=AlertType.choices,
        default=AlertType.LOW_STOCK,
        db_index=True,
        verbose_name=_("Alert Type"),
    )
    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.MEDIUM,
        db_index=True,
        verbose_name=_("Severity"),
    )
    status = models.CharField(
        max_length=30,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        db_index=True,
        verbose_name=_("Alert Status"),
    )

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))

    current_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current Value"))
    threshold_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Threshold Value"))

    triggered_at = models.DateTimeField(db_index=True, verbose_name=_("Triggered At"))

    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged At"))
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="acknowledged_alerts",
        null=True,
        blank=True,
        verbose_name=_("Acknowledged By"),
    )

    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_alerts",
        null=True,
        blank=True,
        verbose_name=_("Resolved By"),
    )
    resolution_notes = models.TextField(blank=True, default="", verbose_name=_("Resolution Notes"))

    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadata"))

    class Meta:
        db_table = "inventory_alerts"
        verbose_name = _("Inventory Alert")
        verbose_name_plural = _("Inventory Alerts")
        ordering = ["-triggered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "alert_number"],
                name="inventory_alert_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "severity"]),
            models.Index(fields=["tenant", "alert_type"]),
            models.Index(fields=["tenant", "medicine"]),
            models.Index(fields=["tenant", "triggered_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.alert_number} - {self.title}"

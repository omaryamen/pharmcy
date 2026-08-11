"""Alert Configuration rules for threshold and warning policies."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class AlertConfiguration(TenantAwareModel, FullAuditModel):
    """Rule definition for automated threshold alerts, expiry lead times, and auto-quarantine policies."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="alert_configurations",
        verbose_name=_("Company"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="alert_configurations",
        null=True,
        blank=True,
        verbose_name=_("Warehouse Scope"),
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="alert_configurations",
        null=True,
        blank=True,
        verbose_name=_("Medicine Scope"),
    )

    rule_name = models.CharField(max_length=150, verbose_name=_("Rule Name"))

    expiry_days_threshold_near = models.PositiveIntegerField(default=90, verbose_name=_("Near Expiry Warning Days"))
    expiry_days_threshold_critical = models.PositiveIntegerField(default=30, verbose_name=_("Critical Expiry Warning Days"))

    reorder_point_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name=_("Reorder Point Alert Trigger Ratio (%)"),
    )

    enable_auto_quarantine_on_recall = models.BooleanField(default=True, verbose_name=_("Enable Auto Quarantine on Recall"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "alert_configurations"
        verbose_name = _("Alert Configuration")
        verbose_name_plural = _("Alert Configurations")
        ordering = ["rule_name"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.rule_name} (Company {self.company.code})"

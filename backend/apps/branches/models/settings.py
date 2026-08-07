"""Branch Settings model for branch-specific operational parameters."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


def default_branch_tax_config() -> dict:
    return {
        "tax_enabled": True,
        "branch_tax_rate_override": None,
        "tax_inclusive": False,
    }


class BranchSettings(FullAuditModel, TenantAwareModel):
    """Operational settings override for a specific Branch."""

    branch = models.OneToOneField(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Branch",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="branch_settings",
        verbose_name="Company",
    )
    working_hours = models.JSONField(default=dict, blank=True, verbose_name="Working hours")
    business_days = models.JSONField(default=list, blank=True, verbose_name="Business days")
    currency_override = models.CharField(max_length=10, blank=True, default="", verbose_name="Currency override")
    receipt_template = models.JSONField(default=dict, blank=True, verbose_name="Receipt template")
    invoice_prefix = models.CharField(max_length=20, blank=True, default="", verbose_name="Invoice prefix")
    tax_settings = models.JSONField(default=default_branch_tax_config, blank=True, verbose_name="Tax settings")
    pos_settings = models.JSONField(default=dict, blank=True, verbose_name="POS settings")
    barcode_settings = models.JSONField(default=dict, blank=True, verbose_name="Barcode settings")
    inventory_settings = models.JSONField(default=dict, blank=True, verbose_name="Inventory settings")
    notification_settings = models.JSONField(default=dict, blank=True, verbose_name="Notification settings")
    printer_settings = models.JSONField(default=dict, blank=True, verbose_name="Printer settings")
    theme_settings = models.JSONField(default=dict, blank=True, verbose_name="Theme settings")

    class Meta:
        verbose_name = "Branch Settings"
        verbose_name_plural = "Branch Settings"

    def __str__(self) -> str:
        return f"Settings for Branch {self.branch.name}"

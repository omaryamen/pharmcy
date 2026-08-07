"""Dosage Form Reference Model."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class DosageForm(FullAuditModel, TenantAwareModel):
    """Pharmaceutical dosage form reference (e.g., Tablet, Capsule, Syrup)."""

    code = models.CharField(max_length=50, verbose_name="Form Code")
    name_en = models.CharField(max_length=100, verbose_name="English Name")
    name_ar = models.CharField(max_length=100, verbose_name="Arabic Name")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["display_order", "name_en"]
        verbose_name = "Dosage Form"
        verbose_name_plural = "Dosage Forms"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_dosageform_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} / {self.name_ar}"

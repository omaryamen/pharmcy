"""Storage Conditions Reference Model."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class StorageCondition(FullAuditModel, TenantAwareModel):
    """Storage environmental condition requirements."""

    code = models.CharField(max_length=50, verbose_name="Condition Code")
    name_en = models.CharField(max_length=150, verbose_name="English Name")
    name_ar = models.CharField(max_length=150, verbose_name="Arabic Name")

    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Min Temp (°C)")
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Max Temp (°C)")

    requires_refrigeration = models.BooleanField(default=False, verbose_name="Requires Refrigeration")
    protect_from_light = models.BooleanField(default=False, verbose_name="Protect From Light")
    humidity_controlled = models.BooleanField(default=False, verbose_name="Humidity Controlled")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        ordering = ["name_en"]
        verbose_name = "Storage Condition"
        verbose_name_plural = "Storage Conditions"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_storage_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} / {self.name_ar}"

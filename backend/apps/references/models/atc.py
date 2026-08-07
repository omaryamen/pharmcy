"""WHO ATC Classification Reference Model (5 Levels)."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class AtcClassification(FullAuditModel, TenantAwareModel):
    """Anatomical Therapeutic Chemical (ATC) Classification 5-level hierarchy."""

    code = models.CharField(max_length=20, verbose_name="ATC Code")
    level = models.PositiveSmallIntegerField(verbose_name="ATC Level (1-5)")
    name_en = models.CharField(max_length=200, verbose_name="English Name")
    name_ar = models.CharField(max_length=200, verbose_name="Arabic Name")

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent ATC Code",
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        ordering = ["code"]
        verbose_name = "ATC Classification"
        verbose_name_plural = "ATC Classifications"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_atc_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name_en}"

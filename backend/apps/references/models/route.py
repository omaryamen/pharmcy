"""Route of Administration Reference Model."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class RouteOfAdministration(FullAuditModel, TenantAwareModel):
    """Route of Administration (e.g., Oral, IV, IM, SC, Topical, Ophthalmic)."""

    code = models.CharField(max_length=30, verbose_name="Route Code")
    name_en = models.CharField(max_length=100, verbose_name="English Name")
    name_ar = models.CharField(max_length=100, verbose_name="Arabic Name")
    abbreviation = models.CharField(max_length=20, blank=True, default="", verbose_name="Abbreviation")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["name_en"]
        verbose_name = "Route of Administration"
        verbose_name_plural = "Routes of Administration"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_route_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} ({self.abbreviation or self.code})"

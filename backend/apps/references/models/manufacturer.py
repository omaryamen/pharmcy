"""Manufacturer Reference Model."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class Manufacturer(FullAuditModel, TenantAwareModel):
    """Pharmaceutical Manufacturer reference entity."""

    code = models.CharField(max_length=50, verbose_name="Manufacturer Code")
    legal_name = models.CharField(max_length=200, verbose_name="Legal Name")
    display_name = models.CharField(max_length=200, verbose_name="Display Name")
    country_of_origin = models.CharField(max_length=100, default="Yemen", verbose_name="Country of Origin")

    address = models.TextField(blank=True, default="", verbose_name="Address")
    website = models.URLField(blank=True, default="", verbose_name="Website")
    contact_email = models.EmailField(blank=True, default="", verbose_name="Contact Email")
    contact_phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Contact Phone")
    registration_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Registration Number")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        ordering = ["display_name"]
        verbose_name = "Manufacturer"
        verbose_name_plural = "Manufacturers"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_manufacturer_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.country_of_origin})"

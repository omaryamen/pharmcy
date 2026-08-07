"""Tax Category Reference Model."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class TaxCategory(FullAuditModel, TenantAwareModel):
    """Tax Category and Tax Rate reference."""

    code = models.CharField(max_length=30, verbose_name="Tax Code")
    name_en = models.CharField(max_length=100, verbose_name="English Name")
    name_ar = models.CharField(max_length=100, verbose_name="Arabic Name")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Tax Rate %")
    is_exempt = models.BooleanField(default=False, verbose_name="Is Exempt")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["code"]
        verbose_name = "Tax Category"
        verbose_name_plural = "Tax Categories"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_taxcategory_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} ({self.tax_rate}%)"

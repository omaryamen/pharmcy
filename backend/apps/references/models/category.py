"""Medicine Category Model with hierarchical tree support."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class MedicineCategory(FullAuditModel, TenantAwareModel):
    """Pharmaceutical product classification category tree."""

    code = models.CharField(max_length=50, verbose_name="Category Code")
    name_en = models.CharField(max_length=150, verbose_name="English Name")
    name_ar = models.CharField(max_length=150, verbose_name="Arabic Name")
    slug = models.SlugField(max_length=150, verbose_name="Slug")

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Category",
    )
    icon = models.CharField(max_length=100, blank=True, default="", verbose_name="Icon")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["display_order", "name_en"]
        verbose_name = "Medicine Category"
        verbose_name_plural = "Medicine Categories"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_category_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} / {self.name_ar} ({self.code})"

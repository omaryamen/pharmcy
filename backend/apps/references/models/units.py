"""Strength Units, Units of Measure (UOM), and Package Types models."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class StrengthUnit(FullAuditModel, TenantAwareModel):
    """Strength units (e.g., mg, mcg, g, ml, %, IU, mEq)."""

    code = models.CharField(max_length=30, verbose_name="Unit Code")
    name_en = models.CharField(max_length=50, verbose_name="English Name")
    name_ar = models.CharField(max_length=50, verbose_name="Arabic Name")
    symbol = models.CharField(max_length=20, verbose_name="Symbol")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["code"]
        verbose_name = "Strength Unit"
        verbose_name_plural = "Strength Units"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_strengthunit_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.symbol} ({self.name_en})"


class UnitOfMeasure(FullAuditModel, TenantAwareModel):
    """Unit of Measure (e.g., Piece, Box, Strip, Bottle, Ampoule)."""

    code = models.CharField(max_length=30, verbose_name="UOM Code")
    name_en = models.CharField(max_length=50, verbose_name="English Name")
    name_ar = models.CharField(max_length=50, verbose_name="Arabic Name")
    symbol = models.CharField(max_length=20, blank=True, default="", verbose_name="Symbol")
    unit_type = models.CharField(max_length=30, default="both", verbose_name="Unit Type")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["name_en"]
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_uom_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} / {self.name_ar}"


class PackageType(FullAuditModel, TenantAwareModel):
    """Package Type reference (e.g., Bottle, Box, Blister, Tube, Strip)."""

    code = models.CharField(max_length=30, verbose_name="Package Code")
    name_en = models.CharField(max_length=50, verbose_name="English Name")
    name_ar = models.CharField(max_length=50, verbose_name="Arabic Name")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_system = models.BooleanField(default=False, verbose_name="Is System Standard")

    class Meta:
        ordering = ["name_en"]
        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="references_packagetype_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name_en} / {self.name_ar}"

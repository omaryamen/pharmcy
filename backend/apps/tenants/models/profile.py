"""Tenant profile model containing legal, contact, and regional preferences."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class BusinessType(models.TextChoices):
    INDEPENDENT_PHARMACY = "independent_pharmacy", _("Independent Pharmacy")
    PHARMACY_CHAIN = "pharmacy_chain", _("Pharmacy Chain")
    DISTRIBUTOR_WAREHOUSE = "distributor_warehouse", _("Distributor / Warehouse")
    CLINIC_PHARMACY = "clinic_pharmacy", _("Clinic / Hospital Pharmacy")


class TenantProfile(FullAuditModel):
    """Extended operational and legal details for a tenant."""

    tenant = models.OneToOneField(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Tenant",
    )
    legal_name = models.CharField(max_length=200, verbose_name="Legal name")
    display_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Display name")
    business_type = models.CharField(
        max_length=50,
        choices=BusinessType.choices,
        default=BusinessType.INDEPENDENT_PHARMACY,
        verbose_name="Business type",
    )
    tax_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Tax number")
    registration_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Registration number")
    country = models.CharField(max_length=100, default="Yemen", verbose_name="Country")
    city = models.CharField(max_length=100, blank=True, default="", verbose_name="City")
    address = models.TextField(blank=True, default="", verbose_name="Address")
    phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Phone")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    website = models.URLField(blank=True, default="", verbose_name="Website")
    logo = models.ImageField(upload_to="tenant_logos/", null=True, blank=True, verbose_name="Logo")
    timezone = models.CharField(max_length=64, default="UTC", verbose_name="Timezone")
    language = models.CharField(max_length=10, default="en", verbose_name="Language")
    currency = models.CharField(max_length=10, default="YER", verbose_name="Currency")
    date_format = models.CharField(max_length=20, default="YYYY-MM-DD", verbose_name="Date format")
    time_format = models.CharField(max_length=20, default="24h", verbose_name="Time format")
    fiscal_year_start_month = models.PositiveSmallIntegerField(default=1, verbose_name="Fiscal year start month")

    class Meta:
        ordering = ["legal_name"]
        verbose_name = "Tenant Profile"
        verbose_name_plural = "Tenant Profiles"

    def __str__(self) -> str:
        return f"Profile for {self.legal_name}"

"""Company model representing the legal business entity owned by a Tenant."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class CompanyStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    SUSPENDED = "suspended", _("Suspended")
    ARCHIVED = "archived", _("Archived")


class CompanyBusinessType(models.TextChoices):
    PHARMACY_GROUP = "pharmacy_group", _("Pharmacy Group / Chain")
    RETAIL_PHARMACY = "retail_pharmacy", _("Retail Pharmacy")
    WHOLESALE_DISTRIBUTOR = "wholesale_distributor", _("Wholesale Distributor")
    CLINIC_NETWORK = "clinic_network", _("Clinic / Hospital Network")
    SINGLE_STORE = "single_store", _("Single Store")


class Company(FullAuditModel, TenantAwareModel):
    """Legal entity owned by a Tenant. Enforces unique names per Tenant."""

    legal_name = models.CharField(max_length=200, verbose_name="Legal name")
    commercial_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Commercial name")
    code = models.CharField(max_length=50, verbose_name="Code")
    slug = models.SlugField(max_length=100, verbose_name="Slug")

    business_type = models.CharField(
        max_length=50,
        choices=CompanyBusinessType.choices,
        default=CompanyBusinessType.RETAIL_PHARMACY,
        verbose_name="Business type",
    )
    license_number = models.CharField(max_length=100, blank=True, default="", verbose_name="License number")
    tax_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Tax number")
    commercial_registration = models.CharField(
        max_length=100, blank=True, default="", verbose_name="Commercial registration"
    )
    vat_registration = models.CharField(max_length=100, blank=True, default="", verbose_name="VAT registration")

    country = models.CharField(max_length=100, default="Yemen", verbose_name="Country")
    city = models.CharField(max_length=100, blank=True, default="", verbose_name="City")
    state = models.CharField(max_length=100, blank=True, default="", verbose_name="State")
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name="Postal code")
    address = models.TextField(blank=True, default="", verbose_name="Address")

    phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Phone")
    mobile = models.CharField(max_length=32, blank=True, default="", verbose_name="Mobile")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    website = models.URLField(blank=True, default="", verbose_name="Website")
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True, verbose_name="Logo")

    primary_color = models.CharField(max_length=20, default="#007bff", verbose_name="Primary color")
    secondary_color = models.CharField(max_length=20, default="#6c757d", verbose_name="Secondary color")

    currency = models.CharField(max_length=10, default="YER", verbose_name="Currency")
    timezone = models.CharField(max_length=64, default="UTC", verbose_name="Timezone")
    language = models.CharField(max_length=10, default="en", verbose_name="Language")
    fiscal_year_start_month = models.PositiveSmallIntegerField(default=1, verbose_name="Fiscal year start month")
    business_hours = models.JSONField(default=dict, blank=True, verbose_name="Business hours")

    status = models.CharField(
        max_length=30,
        choices=CompanyStatus.choices,
        default=CompanyStatus.DRAFT,
        db_index=True,
        verbose_name="Status",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Notes")

    class Meta:
        ordering = ["legal_name"]
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "legal_name"], name="companies_company_tenant_legal_name_uniq"),
            models.UniqueConstraint(fields=["tenant", "code"], name="companies_company_tenant_code_uniq"),
            models.UniqueConstraint(fields=["tenant", "slug"], name="companies_company_tenant_slug_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.legal_name} ({self.tenant.name})"

    def activate(self) -> None:
        self.status = CompanyStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = CompanyStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def suspend(self) -> None:
        self.status = CompanyStatus.SUSPENDED
        self.save(update_fields=["status", "updated_at"])

    def archive(self) -> None:
        self.status = CompanyStatus.ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = CompanyStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])

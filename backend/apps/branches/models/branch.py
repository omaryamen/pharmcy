"""Branch model representing a physical pharmacy or warehouse location."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class BranchStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    TEMPORARILY_CLOSED = "temporarily_closed", _("Temporarily Closed")
    SUSPENDED = "suspended", _("Suspended")
    ARCHIVED = "archived", _("Archived")


class BranchType(models.TextChoices):
    RETAIL_PHARMACY = "retail_pharmacy", _("Retail Pharmacy")
    WAREHOUSE = "warehouse", _("Warehouse")
    DISTRIBUTION_CENTER = "distribution_center", _("Distribution Center")
    HEAD_OFFICE = "head_office", _("Head Office")
    CLINIC_PHARMACY = "clinic_pharmacy", _("Clinic Pharmacy")
    HOSPITAL_PHARMACY = "hospital_pharmacy", _("Hospital Pharmacy")
    VIRTUAL_BRANCH = "virtual_branch", _("Virtual Branch")


class Branch(FullAuditModel, TenantAwareModel):
    """Physical pharmacy or warehouse branch belonging to a Company and Tenant."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="branches",
        verbose_name="Company",
        db_index=True,
    )
    code = models.CharField(max_length=50, verbose_name="Branch code")
    name = models.CharField(max_length=200, verbose_name="Branch name")
    display_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Display name")
    slug = models.SlugField(max_length=100, verbose_name="Slug")

    branch_type = models.CharField(
        max_length=50,
        choices=BranchType.choices,
        default=BranchType.RETAIL_PHARMACY,
        verbose_name="Branch type",
    )
    status = models.CharField(
        max_length=30,
        choices=BranchStatus.choices,
        default=BranchStatus.DRAFT,
        db_index=True,
        verbose_name="Status",
    )
    description = models.TextField(blank=True, default="", verbose_name="Description")

    phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Phone")
    mobile = models.CharField(max_length=32, blank=True, default="", verbose_name="Mobile")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    website = models.URLField(blank=True, default="", verbose_name="Website")

    country = models.CharField(max_length=100, default="Yemen", verbose_name="Country")
    city = models.CharField(max_length=100, blank=True, default="", verbose_name="City")
    state = models.CharField(max_length=100, blank=True, default="", verbose_name="State")
    district = models.CharField(max_length=100, blank=True, default="", verbose_name="District")
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name="Postal code")
    full_address = models.TextField(blank=True, default="", verbose_name="Full address")

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")
    google_maps_link = models.URLField(blank=True, default="", verbose_name="Google Maps link")

    timezone = models.CharField(max_length=64, default="UTC", verbose_name="Timezone")
    working_days = models.JSONField(default=list, blank=True, verbose_name="Working days")
    working_hours = models.JSONField(default=dict, blank=True, verbose_name="Working hours")

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
        verbose_name="Branch manager",
    )
    logo = models.ImageField(upload_to="branch_logos/", null=True, blank=True, verbose_name="Logo")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")

    class Meta:
        ordering = ["name"]
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        constraints = [
            models.UniqueConstraint(fields=["company", "name"], name="branches_branch_company_name_uniq"),
            models.UniqueConstraint(fields=["company", "code"], name="branches_branch_company_code_uniq"),
            models.UniqueConstraint(fields=["company", "slug"], name="branches_branch_company_slug_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.company.legal_name})"

    def activate(self) -> None:
        self.status = BranchStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = BranchStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def suspend(self) -> None:
        self.status = BranchStatus.SUSPENDED
        self.save(update_fields=["status", "updated_at"])

    def archive(self) -> None:
        self.status = BranchStatus.ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = BranchStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])

"""Supplier Domain Model representing commercial vendors and distributors."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class SupplierStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    SUSPENDED = "suspended", _("Suspended")
    BLACKLISTED = "blacklisted", _("Blacklisted")
    ARCHIVED = "archived", _("Archived")


class SupplierType(models.TextChoices):
    MANUFACTURER = "manufacturer", _("Manufacturer")
    DISTRIBUTOR = "distributor", _("Distributor")
    WHOLESALER = "wholesaler", _("Wholesaler")
    IMPORTER = "importer", _("Importer")
    AGENT = "agent", _("Agent")
    SERVICE_PROVIDER = "service_provider", _("Service Provider")


class RiskLevel(models.TextChoices):
    LOW = "low", _("Low Risk")
    MEDIUM = "medium", _("Medium Risk")
    HIGH = "high", _("High Risk")
    CRITICAL = "critical", _("Critical Risk")


class Supplier(FullAuditModel, TenantAwareModel):
    """Enterprise Supplier Entity."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="suppliers",
        null=True,
        blank=True,
        verbose_name="Company",
        db_index=True,
    )
    code = models.CharField(max_length=50, verbose_name="Supplier code")
    legal_name = models.CharField(max_length=255, verbose_name="Legal name")
    display_name = models.CharField(max_length=255, verbose_name="Display name")
    supplier_type = models.CharField(
        max_length=40,
        choices=SupplierType.choices,
        default=SupplierType.DISTRIBUTOR,
        verbose_name="Supplier type",
    )
    supplier_category = models.CharField(max_length=100, default="Pharmaceuticals", verbose_name="Supplier category")

    registration_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Registration number")
    tax_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Tax number")
    vat_number = models.CharField(max_length=100, blank=True, default="", verbose_name="VAT number")

    status = models.CharField(
        max_length=30,
        choices=SupplierStatus.choices,
        default=SupplierStatus.ACTIVE,
        db_index=True,
        verbose_name="Status",
    )

    logo = models.ImageField(upload_to="supplier_logos/", null=True, blank=True, verbose_name="Logo")
    website = models.URLField(blank=True, default="", verbose_name="Website")
    description = models.TextField(blank=True, default="", verbose_name="Description")

    # Contact Information
    primary_contact_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Primary contact name")
    secondary_contact_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Secondary contact name")
    phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Phone")
    mobile = models.CharField(max_length=32, blank=True, default="", verbose_name="Mobile")
    whatsapp = models.CharField(max_length=32, blank=True, default="", verbose_name="WhatsApp")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    support_email = models.EmailField(blank=True, default="", verbose_name="Support email")
    fax = models.CharField(max_length=32, blank=True, default="", verbose_name="Fax")

    # Address Information
    country = models.CharField(max_length=100, default="Yemen", verbose_name="Country")
    state = models.CharField(max_length=100, blank=True, default="", verbose_name="State")
    city = models.CharField(max_length=100, default="Sanaa", verbose_name="City")
    district = models.CharField(max_length=100, blank=True, default="", verbose_name="District")
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name="Postal code")
    street = models.CharField(max_length=255, blank=True, default="", verbose_name="Street")
    building = models.CharField(max_length=100, blank=True, default="", verbose_name="Building")
    google_maps_url = models.URLField(blank=True, default="", verbose_name="Google Maps URL")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Longitude")

    # Financial Information
    default_currency = models.CharField(max_length=10, default="YER", verbose_name="Default currency")
    payment_terms = models.CharField(max_length=100, default="Net 30", verbose_name="Payment terms")
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Credit limit")
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Opening balance")
    current_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Current balance")
    preferred_payment_method = models.CharField(max_length=50, default="bank_transfer", verbose_name="Preferred payment method")
    bank_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Bank name")
    bank_account = models.CharField(max_length=100, blank=True, default="", verbose_name="Bank account")
    iban = models.CharField(max_length=50, blank=True, default="", verbose_name="IBAN")
    swift = models.CharField(max_length=30, blank=True, default="", verbose_name="SWIFT code")
    tax_category = models.CharField(max_length=50, default="standard", verbose_name="Tax category")

    # Licensing & Risk Information
    business_license = models.CharField(max_length=100, blank=True, default="", verbose_name="Business license")
    commercial_registration = models.CharField(max_length=100, blank=True, default="", verbose_name="Commercial registration")
    drug_license = models.CharField(max_length=100, blank=True, default="", verbose_name="Drug license")
    license_expiry_date = models.DateField(null=True, blank=True, verbose_name="License expiry date")
    insurance_info = models.TextField(blank=True, default="", verbose_name="Insurance information")
    is_preferred = models.BooleanField(default=False, verbose_name="Is preferred supplier")
    is_blacklisted = models.BooleanField(default=False, verbose_name="Is blacklisted")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, verbose_name="Rating (1-5)")
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        verbose_name="Risk level",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Notes")

    class Meta:
        ordering = ["display_name"]
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="suppliers_supplier_tenant_code_uniq"),
            models.UniqueConstraint(fields=["tenant", "legal_name"], name="suppliers_supplier_tenant_legal_name_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.code})"

    def activate(self) -> None:
        self.status = SupplierStatus.ACTIVE
        self.is_blacklisted = False
        self.save(update_fields=["status", "is_blacklisted", "updated_at"])

    def suspend(self) -> None:
        self.status = SupplierStatus.SUSPENDED
        self.save(update_fields=["status", "updated_at"])

    def blacklist(self) -> None:
        self.status = SupplierStatus.BLACKLISTED
        self.is_blacklisted = True
        self.save(update_fields=["status", "is_blacklisted", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = SupplierStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])

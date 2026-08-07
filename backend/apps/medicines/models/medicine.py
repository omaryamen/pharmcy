"""Medicine Master Model representing the single source of truth pharmaceutical catalog."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class MedicineStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    DISCONTINUED = "discontinued", _("Discontinued")
    ARCHIVED = "archived", _("Archived")


class PrescriptionType(models.TextChoices):
    OTC = "otc", _("Over The Counter (OTC)")
    PRESCRIPTION_ONLY = "prescription_only", _("Prescription Only (Rx)")
    CONTROLLED = "controlled", _("Controlled Drug")
    NARCOTIC = "narcotic", _("Narcotic")


class MedicineType(models.TextChoices):
    ALLOPATHIC = "allopathic", _("Allopathic")
    HERBAL = "herbal", _("Herbal")
    HOMEOPATHIC = "homeopathic", _("Homeopathic")
    SUPPLEMENT = "supplement", _("Nutritional Supplement")
    MEDICAL_DEVICE = "medical_device", _("Medical Device")


class PregnancyCategory(models.TextChoices):
    A = "A", _("Category A - Controlled studies show no risk")
    B = "B", _("Category B - No evidence of risk in humans")
    C = "C", _("Category C - Risk cannot be ruled out")
    D = "D", _("Category D - Positive evidence of risk")
    X = "X", _("Category X - Contraindicated in pregnancy")
    N = "N", _("Category N - Not classified")


class Medicine(FullAuditModel, TenantAwareModel):
    """Pharmaceutical Master Catalog Product representing master specification."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="medicines",
        null=True,
        blank=True,
        verbose_name="Company",
        db_index=True,
    )
    code = models.CharField(max_length=50, verbose_name="Medicine code")
    sku = models.CharField(max_length=100, verbose_name="SKU")
    barcode = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name="Barcode")
    qr_code = models.CharField(max_length=255, blank=True, default="", verbose_name="QR code")

    arabic_name = models.CharField(max_length=255, verbose_name="Arabic name")
    english_name = models.CharField(max_length=255, verbose_name="English name")
    generic_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Generic name")
    scientific_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Scientific name")
    brand_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Brand name")
    commercial_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Commercial name")
    short_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Short name")
    slug = models.SlugField(max_length=255, verbose_name="Slug")
    search_keywords = models.TextField(blank=True, default="", verbose_name="Search keywords")

    description = models.TextField(blank=True, default="", verbose_name="Description")
    image = models.ImageField(upload_to="medicine_images/", null=True, blank=True, verbose_name="Image")
    status = models.CharField(
        max_length=30,
        choices=MedicineStatus.choices,
        default=MedicineStatus.ACTIVE,
        db_index=True,
        verbose_name="Status",
    )

    # Classification
    therapeutic_class = models.CharField(max_length=150, blank=True, default="", verbose_name="Therapeutic class")
    pharmacological_class = models.CharField(max_length=150, blank=True, default="", verbose_name="Pharmacological class")
    atc_code = models.CharField(max_length=50, blank=True, default="", verbose_name="ATC code")
    category = models.CharField(max_length=100, blank=True, default="", verbose_name="Category")
    category_ref = models.ForeignKey(
        "references.MedicineCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Category Reference",
    )
    prescription_type = models.CharField(
        max_length=30,
        choices=PrescriptionType.choices,
        default=PrescriptionType.PRESCRIPTION_ONLY,
        verbose_name="Prescription type",
    )
    controlled_drug_schedule = models.CharField(max_length=50, blank=True, default="", verbose_name="Controlled drug schedule")
    medicine_type = models.CharField(
        max_length=30,
        choices=MedicineType.choices,
        default=MedicineType.ALLOPATHIC,
        verbose_name="Medicine type",
    )
    drug_classification = models.CharField(max_length=150, blank=True, default="", verbose_name="Drug classification")
    drug_family = models.CharField(max_length=150, blank=True, default="", verbose_name="Drug family")

    # Manufacturer & Registration
    manufacturer_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Manufacturer name")
    manufacturer_ref = models.ForeignKey(
        "references.Manufacturer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Manufacturer Reference",
    )
    country_of_origin = models.CharField(max_length=100, default="Yemen", verbose_name="Country of origin")
    marketing_company = models.CharField(max_length=200, blank=True, default="", verbose_name="Marketing company")
    registration_authority = models.CharField(max_length=150, blank=True, default="", verbose_name="Registration authority")
    registration_number = models.CharField(max_length=100, blank=True, default="", verbose_name="Registration number")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Approval date")
    expiry_of_registration = models.DateField(null=True, blank=True, verbose_name="Expiry of registration")

    # Dosage & Packaging
    dosage_form = models.CharField(max_length=100, default="Tablet", verbose_name="Dosage form")
    dosage_form_ref = models.ForeignKey(
        "references.DosageForm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Dosage Form Reference",
    )
    strength = models.CharField(max_length=50, blank=True, default="", verbose_name="Strength")
    strength_unit = models.CharField(max_length=30, blank=True, default="", verbose_name="Strength unit")
    concentration = models.CharField(max_length=50, blank=True, default="", verbose_name="Concentration")
    route_of_administration = models.CharField(max_length=100, default="Oral", verbose_name="Route of administration")
    package_size = models.PositiveIntegerField(default=1, verbose_name="Package size")
    package_type = models.CharField(max_length=50, default="Box", verbose_name="Package type")
    unit_of_measure = models.CharField(max_length=30, default="Pcs", verbose_name="Unit of measure")
    unit_of_measure_ref = models.ForeignKey(
        "references.UnitOfMeasure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Unit of Measure Reference",
    )
    minimum_dispensing_unit = models.CharField(max_length=30, default="Pcs", verbose_name="Minimum dispensing unit")

    # Medical Information
    indications = models.TextField(blank=True, default="", verbose_name="Indications")
    contraindications = models.TextField(blank=True, default="", verbose_name="Contraindications")
    warnings = models.TextField(blank=True, default="", verbose_name="Warnings")
    precautions = models.TextField(blank=True, default="", verbose_name="Precautions")
    side_effects = models.TextField(blank=True, default="", verbose_name="Side effects")
    storage_conditions = models.CharField(max_length=200, default="Store below 25°C in a dry place", verbose_name="Storage conditions")
    pregnancy_category = models.CharField(
        max_length=10,
        choices=PregnancyCategory.choices,
        default=PregnancyCategory.N,
        verbose_name="Pregnancy category",
    )
    lactation_warning = models.TextField(blank=True, default="", verbose_name="Lactation warning")
    breastfeeding_safety = models.TextField(blank=True, default="", verbose_name="Breastfeeding safety")
    pediatric_usage = models.TextField(blank=True, default="", verbose_name="Pediatric usage")
    geriatric_usage = models.TextField(blank=True, default="", verbose_name="Geriatric usage")
    maximum_daily_dose = models.CharField(max_length=100, blank=True, default="", verbose_name="Maximum daily dose")

    # Drug Safety Flags
    is_high_alert = models.BooleanField(default=False, verbose_name="High alert drug")
    is_lasa = models.BooleanField(default=False, verbose_name="LASA drug")
    is_narcotic = models.BooleanField(default=False, verbose_name="Narcotic drug")
    is_psychotropic = models.BooleanField(default=False, verbose_name="Psychotropic drug")
    is_refrigerated = models.BooleanField(default=False, verbose_name="Refrigerated storage")
    is_hazardous = models.BooleanField(default=False, verbose_name="Hazardous drug")
    is_cold_chain_required = models.BooleanField(default=False, verbose_name="Cold chain required")
    is_light_sensitive = models.BooleanField(default=False, verbose_name="Light sensitive")
    is_controlled_substance = models.BooleanField(default=False, verbose_name="Controlled substance")

    # Commercial Information
    default_purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Default purchase price")
    default_selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Default selling price")
    suggested_retail_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Suggested retail price")
    tax_category = models.CharField(max_length=50, default="standard", verbose_name="Tax category")
    tax_category_ref = models.ForeignKey(
        "references.TaxCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
        verbose_name="Tax Category Reference",
    )
    default_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Default profit margin %")
    is_insurance_eligible = models.BooleanField(default=True, verbose_name="Insurance eligible")
    is_discount_eligible = models.BooleanField(default=True, verbose_name="Discount eligible")
    is_return_eligible = models.BooleanField(default=True, verbose_name="Return eligible")
    is_price_editable = models.BooleanField(default=True, verbose_name="Price editable")

    class Meta:
        ordering = ["english_name"]
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="medicines_medicine_tenant_code_uniq"),
            models.UniqueConstraint(fields=["tenant", "sku"], name="medicines_medicine_tenant_sku_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.english_name} / {self.arabic_name} ({self.code})"

    def activate(self) -> None:
        self.status = MedicineStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = MedicineStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def archive(self) -> None:
        self.status = MedicineStatus.ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = MedicineStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])

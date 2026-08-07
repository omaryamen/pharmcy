"""Pharmaceutical Reference Data Service for managing master reference catalogs."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils.text import slugify

from apps.references.exceptions import CategoryParentLoopError, DuplicateReferenceCodeError
from apps.references.models import (
    AtcClassification,
    DosageForm,
    Manufacturer,
    MedicineCategory,
    PackageType,
    RouteOfAdministration,
    StorageCondition,
    StrengthUnit,
    TaxCategory,
    UnitOfMeasure,
)
from apps.references.repositories import MedicineCategoryRepository

logger = logging.getLogger(__name__)


class ReferenceDataService:
    def __init__(self) -> None:
        self.category_repository = MedicineCategoryRepository()

    @transaction.atomic
    def create_category(
        self,
        tenant,
        *,
        code: str,
        name_en: str,
        name_ar: str,
        parent=None,
        icon: str = "",
        display_order: int = 0,
    ) -> MedicineCategory:
        clean_code = code.lower().strip()
        if self.category_repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateReferenceCodeError(f"Category with code '{clean_code}' already exists.")

        if parent:
            if parent.tenant_id != tenant.pk:
                raise CategoryParentLoopError("Parent category belongs to a different tenant.")

        slug = slugify(name_en or clean_code)
        category = self.category_repository.create(
            tenant=tenant,
            code=clean_code,
            name_en=name_en,
            name_ar=name_ar,
            slug=slug,
            parent=parent,
            icon=icon,
            display_order=display_order,
        )
        logger.info("Created category %s (%s) for tenant %s", category.name_en, category.code, tenant.slug)
        return category

    @transaction.atomic
    def create_manufacturer(
        self,
        tenant,
        *,
        code: str,
        legal_name: str,
        display_name: str,
        country_of_origin: str = "Yemen",
        **extra_fields,
    ) -> Manufacturer:
        clean_code = code.lower().strip()
        if Manufacturer.objects.filter(tenant=tenant, code=clean_code, is_deleted=False).exists():
            raise DuplicateReferenceCodeError(f"Manufacturer with code '{clean_code}' already exists.")

        manufacturer = Manufacturer.objects.create(
            tenant=tenant,
            code=clean_code,
            legal_name=legal_name,
            display_name=display_name,
            country_of_origin=country_of_origin,
            **extra_fields,
        )
        logger.info("Created manufacturer %s (%s) for tenant %s", manufacturer.display_name, manufacturer.code, tenant.slug)
        return manufacturer

    @transaction.atomic
    def seed_system_defaults(self, tenant) -> dict:
        """Seed default pharmaceutical reference data into a tenant catalog."""
        dosage_forms_data = [
            ("tablet", "Tablet", "أقراص"),
            ("capsule", "Capsule", "كبسولات"),
            ("injection", "Injection", "حقن"),
            ("cream", "Cream", "كريم"),
            ("ointment", "Ointment", "مرهم"),
            ("gel", "Gel", "جل"),
            ("drops", "Drops", "قطرة"),
            ("suppository", "Suppository", "تحاميل"),
            ("patch", "Patch", "لاصقة طبية"),
            ("spray", "Spray", "بخاخ"),
            ("syrup", "Syrup", "شراب"),
            ("suspension", "Suspension", "معلق"),
            ("powder", "Powder", "بودرة"),
            ("solution", "Solution", "محلول"),
        ]

        seeded_forms = 0
        for code, name_en, name_ar in dosage_forms_data:
            if not DosageForm.objects.filter(tenant=tenant, code=code, is_deleted=False).exists():
                DosageForm.objects.create(tenant=tenant, code=code, name_en=name_en, name_ar=name_ar, is_system=True)
                seeded_forms += 1

        strength_units_data = [
            ("mg", "Milligram", "ملجم", "mg"),
            ("mcg", "Microgram", "ميكروجرام", "mcg"),
            ("g", "Gram", "جرام", "g"),
            ("kg", "Kilogram", "كيلوجرام", "kg"),
            ("ml", "Milliliter", "مليلتر", "ml"),
            ("l", "Liter", "لتر", "L"),
            ("iu", "International Unit", "وحدة دولية", "IU"),
            ("meq", "Milliequivalent", "ميلي مكافئ", "mEq"),
            ("pct", "Percentage", "نسبة مئوية", "%"),
            ("ppm", "Parts Per Million", "جزء في المليون", "ppm"),
        ]

        seeded_units = 0
        for code, name_en, name_ar, symbol in strength_units_data:
            if not StrengthUnit.objects.filter(tenant=tenant, code=code, is_deleted=False).exists():
                StrengthUnit.objects.create(tenant=tenant, code=code, name_en=name_en, name_ar=name_ar, symbol=symbol, is_system=True)
                seeded_units += 1

        routes_data = [
            ("oral", "Oral", "عن طريق الفم", "PO"),
            ("iv", "Intravenous", "وريدي", "IV"),
            ("im", "Intramuscular", "عضلي", "IM"),
            ("sc", "Subcutaneous", "تحت الجلد", "SC"),
            ("topical", "Topical", "موضعي", "TOP"),
            ("ophthalmic", "Ophthalmic", "عيني", "OPH"),
            ("otic", "Otic", "أذني", "OTIC"),
            ("nasal", "Nasal", "أنفي", "NAS"),
            ("rectal", "Rectal", "شرجي", "PR"),
            ("vaginal", "Vaginal", "مهبلي", "PV"),
            ("inhalation", "Inhalation", "استنشاق", "INH"),
        ]

        seeded_routes = 0
        for code, name_en, name_ar, abbrev in routes_data:
            if not RouteOfAdministration.objects.filter(tenant=tenant, code=code, is_deleted=False).exists():
                RouteOfAdministration.objects.create(tenant=tenant, code=code, name_en=name_en, name_ar=name_ar, abbreviation=abbrev, is_system=True)
                seeded_routes += 1

        tax_data = [
            ("standard", "Standard Tax (15%)", "ضريبة قياسية (15%)", 15.00, False),
            ("zero", "Zero Tax (0%)", "ضريبة صفرية (0%)", 0.00, False),
            ("exempt", "Tax Exempt", "معفى من الضريبة", 0.00, True),
        ]

        seeded_taxes = 0
        for code, name_en, name_ar, rate, exempt in tax_data:
            if not TaxCategory.objects.filter(tenant=tenant, code=code, is_deleted=False).exists():
                TaxCategory.objects.create(tenant=tenant, code=code, name_en=name_en, name_ar=name_ar, tax_rate=rate, is_exempt=exempt, is_system=True)
                seeded_taxes += 1

        logger.info("Seeded defaults for tenant %s: %d forms, %d strength units, %d routes, %d tax categories", tenant.slug, seeded_forms, seeded_units, seeded_routes, seeded_taxes)
        return {
            "dosage_forms": seeded_forms,
            "strength_units": seeded_units,
            "routes": seeded_routes,
            "tax_categories": seeded_taxes,
        }

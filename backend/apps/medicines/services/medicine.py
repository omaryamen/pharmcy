"""Medicine Master Data service for catalog management and lifecycle operations."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils.text import slugify

from apps.medicines.exceptions import (
    DuplicateBarcodeError,
    DuplicateMedicineCodeError,
    DuplicateSKUError,
    MedicineDeleteForbiddenError,
    MedicineNotFoundError,
)
from apps.medicines.models import Medicine, MedicineStatus
from apps.medicines.repositories import MedicineRepository
from apps.references.models import DosageForm, Manufacturer, MedicineCategory, TaxCategory, UnitOfMeasure

logger = logging.getLogger(__name__)


class MedicineService:
    def __init__(self) -> None:
        self.repository = MedicineRepository()

    @transaction.atomic
    def create_medicine(
        self,
        tenant,
        *,
        code: str,
        sku: str,
        arabic_name: str,
        english_name: str,
        barcode: str = "",
        company=None,
        generic_name: str = "",
        scientific_name: str = "",
        brand_name: str = "",
        commercial_name: str = "",
        category: str = "",
        category_ref=None,
        manufacturer_name: str = "",
        manufacturer_ref=None,
        dosage_form: str = "Tablet",
        dosage_form_ref=None,
        unit_of_measure: str = "Pcs",
        unit_of_measure_ref=None,
        tax_category: str = "standard",
        tax_category_ref=None,
        strength: str = "",
        strength_unit: str = "",
        default_purchase_price=0.00,
        default_selling_price=0.00,
        suggested_retail_price=0.00,
        **extra_fields,
    ) -> Medicine:
        clean_code = code.lower().strip()
        clean_sku = sku.strip()
        clean_barcode = barcode.strip() if barcode else ""
        clean_slug = slugify(english_name or arabic_name or clean_code)

        # Enforce scientific_name rule
        clean_scientific = scientific_name.strip() or generic_name.strip() or english_name.strip()

        if self.repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateMedicineCodeError(f"A medicine with code '{clean_code}' already exists in this tenant.")
        if self.repository.exists(tenant=tenant, sku=clean_sku):
            raise DuplicateSKUError(f"A medicine with SKU '{clean_sku}' already exists in this tenant.")
        if clean_barcode and self.repository.exists(tenant=tenant, barcode=clean_barcode):
            raise DuplicateBarcodeError(f"A medicine with barcode '{clean_barcode}' already exists in this tenant.")

        # Auto-resolve reference FKs if not passed explicitly
        if not category_ref and category:
            category_ref = MedicineCategory.objects.filter(tenant=tenant, code=category.lower().strip(), is_deleted=False).first()
        if not manufacturer_ref and manufacturer_name:
            manufacturer_ref = Manufacturer.objects.filter(tenant=tenant, code=manufacturer_name.lower().strip(), is_deleted=False).first()
        if not dosage_form_ref and dosage_form:
            dosage_form_ref = DosageForm.objects.filter(tenant=tenant, code=dosage_form.lower().strip(), is_deleted=False).first()
        if not unit_of_measure_ref and unit_of_measure:
            unit_of_measure_ref = UnitOfMeasure.objects.filter(tenant=tenant, code=unit_of_measure.lower().strip(), is_deleted=False).first()
        if not tax_category_ref and tax_category:
            tax_category_ref = TaxCategory.objects.filter(tenant=tenant, code=tax_category.lower().strip(), is_deleted=False).first()

        # Build enterprise search keywords
        atc = extra_fields.get("atc_code", "")
        keywords = f"{english_name} {arabic_name} {generic_name} {clean_scientific} {brand_name} {commercial_name} {clean_code} {clean_sku} {clean_barcode} {atc} {manufacturer_name} {category}".strip()

        medicine = self.repository.create(
            tenant=tenant,
            company=company,
            code=clean_code,
            sku=clean_sku,
            barcode=clean_barcode,
            arabic_name=arabic_name,
            english_name=english_name,
            generic_name=generic_name,
            scientific_name=clean_scientific,
            brand_name=brand_name,
            commercial_name=commercial_name,
            slug=clean_slug,
            search_keywords=keywords,
            category=category,
            category_ref=category_ref,
            manufacturer_name=manufacturer_name,
            manufacturer_ref=manufacturer_ref,
            dosage_form=dosage_form,
            dosage_form_ref=dosage_form_ref,
            unit_of_measure=unit_of_measure,
            unit_of_measure_ref=unit_of_measure_ref,
            tax_category=tax_category,
            tax_category_ref=tax_category_ref,
            strength=strength,
            strength_unit=strength_unit,
            default_purchase_price=default_purchase_price,
            default_selling_price=default_selling_price,
            suggested_retail_price=suggested_retail_price,
            status=MedicineStatus.ACTIVE,
            **extra_fields,
        )

        logger.info("Created medicine master %s (%s / %s) for tenant %s", medicine.english_name, medicine.code, medicine.sku, tenant.slug)
        return medicine

    @transaction.atomic
    def update_medicine(self, medicine: Medicine, **fields) -> Medicine:
        return self.repository.update(medicine, **fields)

    @transaction.atomic
    def activate_medicine(self, medicine: Medicine) -> Medicine:
        medicine.activate()
        logger.info("Activated medicine master %s", medicine.code)
        return medicine

    @transaction.atomic
    def deactivate_medicine(self, medicine: Medicine) -> Medicine:
        medicine.deactivate()
        logger.info("Deactivated medicine master %s", medicine.code)
        return medicine

    @transaction.atomic
    def archive_medicine(self, medicine: Medicine) -> Medicine:
        medicine.archive()
        logger.info("Archived medicine master %s", medicine.code)
        return medicine

    @transaction.atomic
    def restore_medicine(self, medicine: Medicine) -> Medicine:
        medicine.restore()
        logger.info("Restored medicine master %s", medicine.code)
        return medicine

    @transaction.atomic
    def soft_delete_medicine(self, medicine: Medicine) -> Medicine:
        # Check active dependency guard
        has_inventory = getattr(medicine, "inventory_items", None) and medicine.inventory_items.filter(is_deleted=False).exists()
        has_sales = getattr(medicine, "sale_items", None) and medicine.sale_items.filter(is_deleted=False).exists()

        if has_inventory or has_sales:
            raise MedicineDeleteForbiddenError("Cannot delete medicine master record linked to active inventory or sales.")

        self.repository.delete(medicine)
        logger.info("Soft deleted medicine master %s", medicine.code)
        return medicine

    def lookup_by_barcode(self, tenant, barcode: str) -> Medicine:
        medicine = self.repository.get_by_barcode(tenant, barcode)
        if not medicine:
            raise MedicineNotFoundError(f"No medicine found with barcode '{barcode}'.")
        return medicine

    def lookup_by_sku(self, tenant, sku: str) -> Medicine:
        medicine = self.repository.get_by_sku(tenant, sku)
        if not medicine:
            raise MedicineNotFoundError(f"No medicine found with SKU '{sku}'.")
        return medicine

    @transaction.atomic
    def bulk_import_medicines(self, tenant, company, items: list[dict]) -> dict:
        created_count = 0
        errors: list[dict] = []

        for idx, item in enumerate(items):
            try:
                self.create_medicine(
                    tenant=tenant,
                    company=company,
                    code=item["code"],
                    sku=item["sku"],
                    arabic_name=item["arabic_name"],
                    english_name=item["english_name"],
                    barcode=item.get("barcode", ""),
                    dosage_form=item.get("dosage_form", "Tablet"),
                    strength=item.get("strength", ""),
                    default_purchase_price=item.get("default_purchase_price", 0.00),
                    default_selling_price=item.get("default_selling_price", 0.00),
                )
                created_count += 1
            except Exception as exc:  # noqa: BLE001 - collect import errors
                errors.append({"row": idx + 1, "code": item.get("code", ""), "error": str(exc)})

        return {"created": created_count, "errors": errors}

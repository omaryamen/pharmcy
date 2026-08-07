"""Unit & Integration tests for Enterprise Medicine Master Data services."""

import pytest

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.medicines.exceptions import DuplicateBarcodeError, DuplicateMedicineCodeError, DuplicateSKUError, MedicineNotFoundError
from apps.medicines.models import MedicineStatus
from apps.medicines.services import MedicineService


@pytest.mark.django_db
class TestMedicineServices:
    def test_create_medicine_service(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Serv", code="t_med_s", slug="tenant-med-s")
        company = Company.objects.create(tenant=tenant, legal_name="Sheba Pharma", code="sheba_p", slug="sheba-p")
        service = MedicineService()

        medicine = service.create_medicine(
            tenant=tenant,
            company=company,
            code="MED-3003",
            sku="SKU-AUG-625",
            barcode="6291048002022",
            arabic_name="أوجمنتين 625 ملجم",
            english_name="Augmentin 625mg",
            generic_name="Amoxicillin + Clavulanic Acid",
            dosage_form="Tablet",
            strength="625",
            strength_unit="mg",
            default_purchase_price=800.00,
            default_selling_price=1000.00,
        )

        assert medicine.code == "med-3003"
        assert medicine.sku == "SKU-AUG-625"
        assert medicine.status == MedicineStatus.ACTIVE

    def test_duplicate_code_sku_barcode_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Dup", code="t_med_d", slug="tenant-med-d")
        service = MedicineService()

        service.create_medicine(
            tenant=tenant,
            code="MED-DUP-1",
            sku="SKU-DUP-1",
            barcode="BAR123456",
            arabic_name="دواء 1",
            english_name="Medicine 1",
        )

        with pytest.raises(DuplicateMedicineCodeError):
            service.create_medicine(
                tenant=tenant,
                code="MED-DUP-1",
                sku="SKU-OTHER",
                arabic_name="دواء آخر",
                english_name="Other Medicine",
            )

        with pytest.raises(DuplicateSKUError):
            service.create_medicine(
                tenant=tenant,
                code="MED-OTHER",
                sku="SKU-DUP-1",
                arabic_name="دواء آخر",
                english_name="Other Medicine",
            )

        with pytest.raises(DuplicateBarcodeError):
            service.create_medicine(
                tenant=tenant,
                code="MED-OTHER-2",
                sku="SKU-OTHER-2",
                barcode="BAR123456",
                arabic_name="دواء آخر",
                english_name="Other Medicine",
            )

    def test_barcode_and_sku_lookups(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Lookup", code="t_med_lk", slug="tenant-med-lk")
        service = MedicineService()

        medicine = service.create_medicine(
            tenant=tenant,
            code="MED-LK-1",
            sku="SKU-LK-1",
            barcode="7890123456789",
            arabic_name="فيتامين سي",
            english_name="Vitamin C 1000mg",
        )

        by_barcode = service.lookup_by_barcode(tenant, "7890123456789")
        assert by_barcode.pk == medicine.pk

        by_sku = service.lookup_by_sku(tenant, "SKU-LK-1")
        assert by_sku.pk == medicine.pk

        with pytest.raises(MedicineNotFoundError):
            service.lookup_by_barcode(tenant, "NON_EXISTENT")

    def test_bulk_import_medicines(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Import", code="t_med_imp", slug="tenant-med-imp")
        service = MedicineService()

        items = [
            {"code": "IMP-001", "sku": "SKU-IMP-1", "arabic_name": "دواء مستورد 1", "english_name": "Imported Med 1"},
            {"code": "IMP-002", "sku": "SKU-IMP-2", "arabic_name": "دواء مستورد 2", "english_name": "Imported Med 2"},
        ]

        result = service.bulk_import_medicines(tenant, None, items)
        assert result["created"] == 2
        assert len(result["errors"]) == 0

"""Unit tests for Enterprise Medicine Master Data models."""

import pytest

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.medicines.models import Medicine, MedicineStatus, MedicineType, PregnancyCategory, PrescriptionType


@pytest.mark.django_db
class TestMedicineModels:
    def test_create_medicine_master_entry(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Models", code="t_med_m", slug="tenant-med-m")
        company = Company.objects.create(tenant=tenant, legal_name="Yemen Pharma", code="yp", slug="yp")

        medicine = Medicine.objects.create(
            tenant=tenant,
            company=company,
            code="MED-1001",
            sku="SKU-PAN-500",
            barcode="6291048001015",
            arabic_name="بنادول أدڤانس 500 ملجم",
            english_name="Panadol Advance 500mg",
            generic_name="Paracetamol",
            scientific_name="Acetaminophen",
            brand_name="Panadol",
            slug="panadol-advance-500mg",
            status=MedicineStatus.ACTIVE,
            dosage_form="Tablet",
            strength="500",
            strength_unit="mg",
            prescription_type=PrescriptionType.OTC,
            medicine_type=MedicineType.ALLOPATHIC,
            pregnancy_category=PregnancyCategory.B,
            is_refrigerated=False,
            default_purchase_price=150.00,
            default_selling_price=200.00,
        )

        assert medicine.pk is not None
        assert str(medicine) == "Panadol Advance 500mg / بنادول أدڤانس 500 ملجم (MED-1001)"
        assert medicine.tenant == tenant
        assert medicine.company == company
        assert medicine.default_selling_price == 200.00

    def test_medicine_lifecycle_methods(self, db):
        tenant = Tenant.objects.create(name="Tenant Med Life", code="t_med_l", slug="tenant-med-l")
        medicine = Medicine.objects.create(
            tenant=tenant,
            code="MED-2002",
            sku="SKU-AMX-500",
            arabic_name="أموكسيل 500 ملجم",
            english_name="Amoxil 500mg",
            slug="amoxil-500mg",
        )

        assert medicine.status == MedicineStatus.ACTIVE

        medicine.deactivate()
        assert medicine.status == MedicineStatus.INACTIVE

        medicine.archive()
        assert medicine.status == MedicineStatus.ARCHIVED

        medicine.restore()
        assert medicine.status == MedicineStatus.ACTIVE

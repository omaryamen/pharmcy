"""Unit tests for Enterprise Pharmaceutical Reference Data models."""

import pytest

from apps.core.models import Tenant
from apps.references.models import DosageForm, Manufacturer, MedicineCategory, TaxCategory


@pytest.mark.django_db
class TestReferenceModels:
    def test_create_category_and_manufacturer(self, db):
        tenant = Tenant.objects.create(name="Tenant Ref Models", code="t_ref_m", slug="tenant-ref-m")

        cat = MedicineCategory.objects.create(
            tenant=tenant,
            code="analgesics",
            name_en="Analgesics & Pain Relief",
            name_ar="مسكنات الألم",
            slug="analgesics-pain-relief",
        )
        assert cat.pk is not None
        assert str(cat) == "Analgesics & Pain Relief / مسكنات الألم (analgesics)"

        mfr = Manufacturer.objects.create(
            tenant=tenant,
            code="GSK_YEMEN",
            legal_name="GlaxoSmithKline Yemen Ltd",
            display_name="GSK",
            country_of_origin="Yemen",
        )
        assert mfr.pk is not None
        assert str(mfr) == "GSK (Yemen)"

    def test_dosage_form_and_tax_category(self, db):
        tenant = Tenant.objects.create(name="Tenant Ref Types", code="t_ref_t", slug="tenant-ref-t")

        form = DosageForm.objects.create(tenant=tenant, code="tab", name_en="Tablet", name_ar="قرص")
        assert form.name_en == "Tablet"

        tax = TaxCategory.objects.create(tenant=tenant, code="std", name_en="Standard Tax", name_ar="ضريبة قياسية", tax_rate=15.00)
        assert tax.tax_rate == 15.00

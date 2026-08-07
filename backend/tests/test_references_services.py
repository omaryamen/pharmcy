"""Unit & Integration tests for Enterprise Pharmaceutical Reference Data services."""

import pytest

from apps.core.models import Tenant
from apps.references.exceptions import DuplicateReferenceCodeError
from apps.references.models import DosageForm, RouteOfAdministration, StrengthUnit, TaxCategory
from apps.references.services import ReferenceDataService


@pytest.mark.django_db
class TestReferenceServices:
    def test_create_category_and_manufacturer_service(self, db):
        tenant = Tenant.objects.create(name="Tenant Ref Serv", code="t_ref_s", slug="tenant-ref-s")
        service = ReferenceDataService()

        cat = service.create_category(tenant=tenant, code="ANTIBIOTICS", name_en="Antibiotics", name_ar="مضادات حيوية")
        assert cat.code == "antibiotics"

        mfr = service.create_manufacturer(
            tenant=tenant, code="BAYER", legal_name="Bayer Pharma AG", display_name="Bayer", country_of_origin="Germany"
        )
        assert mfr.country_of_origin == "Germany"

    def test_duplicate_category_code_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Ref Dup", code="t_ref_d", slug="tenant-ref-d")
        service = ReferenceDataService()

        service.create_category(tenant=tenant, code="VITAMINS", name_en="Vitamins", name_ar="فيتامينات")

        with pytest.raises(DuplicateReferenceCodeError):
            service.create_category(tenant=tenant, code="VITAMINS", name_en="Vitamins Dup", name_ar="فيتامينات")

    def test_seed_system_defaults(self, db):
        tenant = Tenant.objects.create(name="Tenant Ref Seed", code="t_ref_sd", slug="tenant-ref-sd")
        service = ReferenceDataService()

        result = service.seed_system_defaults(tenant)
        assert result["dosage_forms"] > 0
        assert result["strength_units"] > 0
        assert result["routes"] > 0
        assert result["tax_categories"] > 0

        assert DosageForm.objects.filter(tenant=tenant, code="tablet").exists()
        assert StrengthUnit.objects.filter(tenant=tenant, code="mg").exists()
        assert RouteOfAdministration.objects.filter(tenant=tenant, code="oral").exists()
        assert TaxCategory.objects.filter(tenant=tenant, code="standard").exists()

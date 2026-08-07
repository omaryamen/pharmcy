"""Unit tests for Company Management models."""

import pytest

from apps.companies.models import Company, CompanyBusinessType, CompanySettings, CompanyStatus
from apps.core.models import Tenant, TenantStatus


@pytest.mark.django_db
class TestCompanyModels:
    def test_create_company_and_settings(self, db):
        tenant = Tenant.objects.create(name="Tenant One", code="t1", slug="tenant-1", status=TenantStatus.ACTIVE)

        company = Company.objects.create(
            tenant=tenant,
            legal_name="Al-Shifa Pharmacy LLC",
            commercial_name="Al-Shifa Group",
            code="shifa_01",
            slug="al-shifa-pharmacy-llc",
            business_type=CompanyBusinessType.PHARMACY_GROUP,
            tax_number="TAX-12345",
            commercial_registration="CR-998877",
            status=CompanyStatus.ACTIVE,
        )

        assert company.pk is not None
        assert str(company) == "Al-Shifa Pharmacy LLC (Tenant One)"

        settings_obj = CompanySettings.objects.create(
            company=company,
            tenant=tenant,
            default_currency="YER",
        )
        assert settings_obj.company == company
        assert settings_obj.tax_configuration["default_tax_rate"] == 15.0
        assert settings_obj.document_prefixes["invoice_prefix"] == "INV"

    def test_company_status_lifecycle(self, db):
        tenant = Tenant.objects.create(name="Tenant Two", code="t2", slug="tenant-2")
        company = Company.objects.create(tenant=tenant, legal_name="Beta Med", code="beta_med", slug="beta-med")

        assert company.status == CompanyStatus.DRAFT

        company.activate()
        assert company.status == CompanyStatus.ACTIVE

        company.deactivate()
        assert company.status == CompanyStatus.INACTIVE

        company.suspend()
        assert company.status == CompanyStatus.SUSPENDED

        company.archive()
        assert company.status == CompanyStatus.ARCHIVED

        company.restore()
        assert company.status == CompanyStatus.ACTIVE

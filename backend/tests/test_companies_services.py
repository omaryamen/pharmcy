"""Unit & Integration tests for Company Management services."""

import pytest

from apps.companies.exceptions import DuplicateCompanyNameError
from apps.companies.models import CompanyStatus
from apps.companies.services import CompanyService, CompanySettingsService
from apps.core.models import Tenant


@pytest.mark.django_db
class TestCompanyServices:
    def test_company_creation_and_settings_auto_provisioning(self, db):
        tenant = Tenant.objects.create(name="Tenant A", code="tenant_a", slug="tenant-a")
        service = CompanyService()

        company = service.create_company(
            tenant=tenant,
            legal_name="Al-Hikma Pharma",
            code="hikma_01",
            slug="al-hikma-pharma",
            country="Yemen",
            currency="YER",
        )

        assert company.legal_name == "Al-Hikma Pharma"
        assert company.status == CompanyStatus.ACTIVE
        assert hasattr(company, "settings")
        assert company.settings.default_currency == "YER"

    def test_duplicate_name_or_code_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant B", code="tenant_b", slug="tenant-b")
        service = CompanyService()

        service.create_company(tenant=tenant, legal_name="Unique Pharmacy", code="uniq_pharma", slug="unique-pharma")

        with pytest.raises(DuplicateCompanyNameError):
            service.create_company(tenant=tenant, legal_name="Unique Pharmacy", code="other_code", slug="other-slug")

        with pytest.raises(DuplicateCompanyNameError):
            service.create_company(tenant=tenant, legal_name="Other Name", code="uniq_pharma", slug="other-slug-2")

    def test_company_lifecycle_and_cloning(self, db):
        tenant = Tenant.objects.create(name="Tenant C", code="tenant_c", slug="tenant-c")
        service = CompanyService()

        company = service.create_company(tenant=tenant, legal_name="Parent Company", code="parent_co", slug="parent-co")

        service.suspend_company(company)
        assert company.status == CompanyStatus.SUSPENDED

        service.activate_company(company)
        assert company.status == CompanyStatus.ACTIVE

        cloned = service.clone_company(
            company,
            new_legal_name="Cloned Company",
            new_code="cloned_co",
            new_slug="cloned-co",
        )
        assert cloned.legal_name == "Cloned Company"
        assert cloned.tenant == tenant
        assert cloned.settings.tax_configuration == company.settings.tax_configuration

    def test_company_settings_update(self, db):
        tenant = Tenant.objects.create(name="Tenant D", code="tenant_d", slug="tenant-d")
        company_service = CompanyService()
        settings_service = CompanySettingsService()

        company = company_service.create_company(tenant=tenant, legal_name="Settings Co", code="settings_co", slug="settings-co")

        updated_settings = settings_service.update_settings(
            company,
            tax_configuration={"tax_enabled": True, "default_tax_rate": 10.0},
            document_prefixes={"invoice_prefix": "FACT"},
        )

        assert updated_settings.tax_configuration["default_tax_rate"] == 10.0
        assert updated_settings.document_prefixes["invoice_prefix"] == "FACT"

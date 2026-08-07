"""Tests verifying cross-tenant company data isolation and protection."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.services import CompanyService
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestCompanyIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def company_service(self):
        return CompanyService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha", slug="tenant-alpha", admin_email="owner_a@alpha.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta", slug="tenant-beta", admin_email="owner_b@beta.com")

    def test_tenant_cannot_access_other_tenant_companies(self, tenant_a, tenant_b, company_service):
        company_a = company_service.create_company(tenant=tenant_a, legal_name="Company Alpha", code="co_alpha", slug="co-alpha")
        company_b = company_service.create_company(tenant=tenant_b, legal_name="Company Beta", code="co_beta", slug="co-beta")

        client = APIClient()

        # Authenticate as Owner A with Tenant A header
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/companies/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        ids = [item["id"] for item in data["data"]["results"]]

        assert str(company_a.pk) in ids
        assert str(company_b.pk) not in ids

        # Attempt to access Company B details using Tenant A context
        detail_resp = client.get(f"/api/v1/companies/{company_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_same_company_code_allowed_across_different_tenants(self, tenant_a, tenant_b, company_service):
        comp_a = company_service.create_company(tenant=tenant_a, legal_name="Shared Name", code="shared_code", slug="shared-slug")
        comp_b = company_service.create_company(tenant=tenant_b, legal_name="Shared Name", code="shared_code", slug="shared-slug")

        assert comp_a.pk != comp_b.pk
        assert comp_a.tenant == tenant_a
        assert comp_b.tenant == tenant_b

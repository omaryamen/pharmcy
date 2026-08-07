"""Tests verifying cross-tenant & cross-company branch data isolation."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.branches.services import BranchService
from apps.companies.services import CompanyService
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestBranchIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def company_service(self):
        return CompanyService()

    @pytest.fixture
    def branch_service(self):
        return BranchService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha BR", slug="tenant-alpha-br", admin_email="owner_a@alphabr.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta BR", slug="tenant-beta-br", admin_email="owner_b@betabr.com")

    def test_tenant_cannot_access_other_tenant_branches(self, tenant_a, tenant_b, company_service, branch_service):
        comp_a = company_service.create_company(tenant=tenant_a, legal_name="Company Alpha", code="co_alpha_br", slug="co-alpha-br")
        comp_b = company_service.create_company(tenant=tenant_b, legal_name="Company Beta", code="co_beta_br", slug="co-beta-br")

        branch_a = branch_service.create_branch(tenant=tenant_a, company=comp_a, name="Branch Alpha", code="br_alpha", slug="br-alpha")
        branch_b = branch_service.create_branch(tenant=tenant_b, company=comp_b, name="Branch Beta", code="br_beta", slug="br-beta")

        client = APIClient()
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/branches/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        ids = [item["id"] for item in data["data"]["results"]]

        assert str(branch_a.pk) in ids
        assert str(branch_b.pk) not in ids

        detail_resp = client.get(f"/api/v1/branches/{branch_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_same_branch_code_allowed_in_different_companies(self, tenant_a, company_service, branch_service):
        comp_a1 = company_service.create_company(tenant=tenant_a, legal_name="Company A1", code="co_a1", slug="co-a1")
        comp_a2 = company_service.create_company(tenant=tenant_a, legal_name="Company A2", code="co_a2", slug="co-a2")

        br1 = branch_service.create_branch(tenant=tenant_a, company=comp_a1, name="Main Store", code="main_store", slug="main-store")
        br2 = branch_service.create_branch(tenant=tenant_a, company=comp_a2, name="Main Store", code="main_store", slug="main-store")

        assert br1.pk != br2.pk
        assert br1.company == comp_a1
        assert br2.company == comp_a2

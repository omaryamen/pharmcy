"""Tests verifying cross-tenant, cross-company, and cross-branch user data isolation."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.branches.services import BranchService
from apps.companies.services import CompanyService
from apps.tenants.services import TenantProvisioningService
from apps.users.services import UserService

User = get_user_model()


@pytest.mark.django_db
class TestUserIsolation:
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
    def user_service(self):
        return UserService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha USR", slug="tenant-alpha-usr", admin_email="owner_a@alphausr.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta USR", slug="tenant-beta-usr", admin_email="owner_b@betausr.com")

    def test_tenant_cannot_access_other_tenant_users(self, tenant_a, tenant_b, company_service, branch_service, user_service):
        comp_a = company_service.create_company(tenant=tenant_a, legal_name="Co Alpha", code="co_alpha_u", slug="co-alpha-u")
        comp_b = company_service.create_company(tenant=tenant_b, legal_name="Co Beta", code="co_beta_u", slug="co-beta-u")

        br_a = branch_service.create_branch(tenant=tenant_a, company=comp_a, name="Br Alpha", code="br_a", slug="br-a")
        br_b = branch_service.create_branch(tenant=tenant_b, company=comp_b, name="Br Beta", code="br_b", slug="br-b")

        user_a = user_service.create_enterprise_user(tenant=tenant_a, company=comp_a, primary_branch=br_a, email="user_a@alpha.com", first_name="UserA")
        user_b = user_service.create_enterprise_user(tenant=tenant_b, company=comp_b, primary_branch=br_b, email="user_b@beta.com", first_name="UserB")

        client = APIClient()
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/users/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        emails = [item["email"] for item in data["data"]["results"]]

        assert user_a.email in emails
        assert user_b.email not in emails

        detail_resp = client.get(f"/api/v1/users/{user_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

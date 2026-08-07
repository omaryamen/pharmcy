"""API Integration tests for Enterprise User Management endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.branches.services import BranchService
from apps.companies.services import CompanyService
from apps.rbac.models import Role
from apps.tenants.services import TenantProvisioningService
from apps.users.services import UserService

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant User API",
            slug="main-tenant-user-api",
            admin_email="owner@userapi.com",
            admin_password="Password123!",
        )

    @pytest.fixture
    def company(self, tenant_context):
        return CompanyService().create_company(
            tenant=tenant_context,
            legal_name="Parent User Corp",
            code="parent_u_corp",
            slug="parent-u-corp",
        )

    @pytest.fixture
    def branch(self, tenant_context, company):
        return BranchService().create_branch(
            tenant=tenant_context,
            company=company,
            name="Branch API 1",
            code="br_api_1",
            slug="br-api-1",
        )

    def test_create_and_list_users_api(self, api_client, tenant_context, company, branch):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "email": "newemployee@userapi.com",
            "first_name": "Farouq",
            "last_name": "Al-Attas",
            "password": "SecurePass123!",
            "company_id": str(company.pk),
            "primary_branch_id": str(branch.pk),
            "job_title": "Store Manager",
            "department": "Logistics",
        }
        response = api_client.post("/api/v1/users/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["email"] == "newemployee@userapi.com"

        list_response = api_client.get(f"/api/v1/users/?company={company.pk}", **headers)
        assert list_response.status_code == status.HTTP_200_OK
        list_data = list_response.json()
        assert len(list_data["data"]["results"]) >= 1

    def test_current_user_me_endpoint(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        response = api_client.get("/api/v1/users/me/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["email"] == "owner@userapi.com"

    def test_user_role_assignment_and_status_api(self, api_client, tenant_context, company, branch):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        user = UserService().create_enterprise_user(
            tenant=tenant_context,
            company=company,
            primary_branch=branch,
            email="staff@userapi.com",
            first_name="Staff",
        )
        user_id = str(user.pk)

        role = Role.objects.create(tenant=tenant_context, name="Supervisor", code="supervisor_role")

        # Assign Role
        response = api_client.post(f"/api/v1/users/{user_id}/assign-role/", data={"role_id": str(role.pk)}, format="json", **headers)
        assert response.status_code == status.HTTP_200_OK

        # Lock & Unlock Account
        lock_resp = api_client.post(f"/api/v1/users/{user_id}/lock/", **headers)
        assert lock_resp.status_code == status.HTTP_200_OK
        assert lock_resp.json()["data"]["status"] == "locked"

        unlock_resp = api_client.post(f"/api/v1/users/{user_id}/unlock/", **headers)
        assert unlock_resp.status_code == status.HTTP_200_OK
        assert unlock_resp.json()["data"]["status"] == "active"

"""API Integration tests for Branch Management endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.branches.models import BranchStatus
from apps.branches.services import BranchService
from apps.companies.services import CompanyService
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestBranchAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant Branch API",
            slug="main-tenant-branch-api",
            admin_email="owner@branchapi.com",
            admin_password="Password123!",
        )

    @pytest.fixture
    def company(self, tenant_context):
        return CompanyService().create_company(
            tenant=tenant_context,
            legal_name="Parent Company Ltd",
            code="parent_ltd",
            slug="parent-ltd",
        )

    def test_create_and_list_branches_api(self, api_client, tenant_context, company):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "company": str(company.pk),
            "name": "API Branch One",
            "code": "api_br_1",
            "slug": "api-br-1",
            "branch_type": "retail_pharmacy",
            "city": "Sanaa",
        }
        response = api_client.post("/api/v1/branches/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["name"] == "API Branch One"

        list_response = api_client.get(f"/api/v1/branches/?company={company.pk}", **headers)
        assert list_response.status_code == status.HTTP_200_OK
        list_data = list_response.json()
        assert len(list_data["data"]["results"]) >= 1

    def test_branch_settings_and_stats_api(self, api_client, tenant_context, company):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        branch = BranchService().create_branch(
            tenant=tenant_context,
            company=company,
            name="API Branch Two",
            code="api_br_2",
            slug="api-br-2",
        )
        branch_id = str(branch.pk)

        response = api_client.get(f"/api/v1/branches/{branch_id}/settings/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tax_settings" in data["data"]

        patch_resp = api_client.patch(
            f"/api/v1/branches/{branch_id}/settings/",
            data={"invoice_prefix": "BR2-INV"},
            format="json",
            **headers,
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        patch_data = patch_resp.json()
        assert patch_data["data"]["invoice_prefix"] == "BR2-INV"

        stats_resp = api_client.get(f"/api/v1/branches/{branch_id}/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        stats_data = stats_resp.json()
        assert stats_data["data"]["code"] == "api_br_2"

    def test_branch_status_lifecycle_api(self, api_client, tenant_context, company):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        branch = BranchService().create_branch(
            tenant=tenant_context,
            company=company,
            name="Lifecycle Branch",
            code="api_br_life",
            slug="api-br-life",
        )
        branch_id = str(branch.pk)

        response = api_client.post(f"/api/v1/branches/{branch_id}/suspend/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == BranchStatus.SUSPENDED

        response = api_client.post(f"/api/v1/branches/{branch_id}/activate/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == BranchStatus.ACTIVE

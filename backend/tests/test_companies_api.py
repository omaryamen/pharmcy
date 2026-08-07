"""API Integration tests for Company Management endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import CompanyStatus
from apps.companies.services import CompanyService
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestCompanyAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def superuser(self):
        return User.objects.create_superuser(email="admin@platform.com", first_name="Super", password="Password123!")

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant",
            slug="main-tenant",
            admin_email="owner@maintenant.com",
            admin_password="Password123!",
        )

    def test_create_and_list_companies_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "legal_name": "API Company One",
            "commercial_name": "API Commercial",
            "code": "api_co_1",
            "slug": "api-co-1",
            "country": "Yemen",
            "currency": "YER",
        }
        response = api_client.post("/api/v1/companies/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["legal_name"] == "API Company One"

        list_response = api_client.get("/api/v1/companies/", **headers)
        assert list_response.status_code == status.HTTP_200_OK
        list_data = list_response.json()
        assert len(list_data["data"]["results"]) >= 1

    def test_company_settings_and_stats_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        company = CompanyService().create_company(
            tenant=tenant_context,
            legal_name="API Company Two",
            code="api_co_2",
            slug="api-co-2",
        )
        company_id = str(company.pk)

        response = api_client.get(f"/api/v1/companies/{company_id}/settings/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["default_currency"] == "YER"

        patch_resp = api_client.patch(
            f"/api/v1/companies/{company_id}/settings/",
            data={"default_currency": "USD"},
            format="json",
            **headers,
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        patch_data = patch_resp.json()
        assert patch_data["data"]["default_currency"] == "USD"

        stats_resp = api_client.get(f"/api/v1/companies/{company_id}/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        stats_data = stats_resp.json()
        assert stats_data["data"]["code"] == "api_co_2"

    def test_company_status_lifecycle_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        company = CompanyService().create_company(
            tenant=tenant_context,
            legal_name="API Company Lifecycle",
            code="api_co_life",
            slug="api-co-life",
        )
        company_id = str(company.pk)

        response = api_client.post(f"/api/v1/companies/{company_id}/deactivate/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == CompanyStatus.INACTIVE

        response = api_client.post(f"/api/v1/companies/{company_id}/activate/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == CompanyStatus.ACTIVE

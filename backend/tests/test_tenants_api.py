"""API Integration tests for Tenant Management endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import TenantStatus
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestTenantAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def superuser(self):
        return User.objects.create_superuser(email="admin@platform.com", first_name="Super", password="Password123!")

    @pytest.fixture
    def provisioned_tenant(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="City Pharmacy",
            slug="city-pharmacy",
            admin_email="owner@citypharmacy.com",
            admin_password="Password123!",
        )

    def test_list_tenants_as_superuser(self, api_client, superuser, provisioned_tenant):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/v1/tenants/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) >= 1

    def test_provision_tenant_api(self, api_client, superuser):
        api_client.force_authenticate(user=superuser)
        payload = {
            "name": "New API Tenant",
            "slug": "new-api-tenant",
            "legal_name": "New API Tenant LLC",
            "admin_email": "admin@newapitenant.com",
            "admin_password": "SecurePassword123!",
            "plan": "starter",
        }
        response = api_client.post("/api/v1/tenants/", data=payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["slug"] == "new-api-tenant"

    def test_get_current_tenant_me_profile_and_settings(self, api_client, provisioned_tenant):
        owner = provisioned_tenant.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(provisioned_tenant.pk)}

        response = api_client.get("/api/v1/tenants/me/profile/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["legal_name"] == "City Pharmacy"

        response = api_client.get("/api/v1/tenants/me/settings/", **headers)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get("/api/v1/tenants/me/stats/", **headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["slug"] == "city-pharmacy"

    def test_tenant_lifecycle_api_actions(self, api_client, superuser, provisioned_tenant):
        api_client.force_authenticate(user=superuser)
        tenant_id = str(provisioned_tenant.pk)

        response = api_client.post(f"/api/v1/tenants/{tenant_id}/suspend/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == TenantStatus.SUSPENDED

        response = api_client.post(f"/api/v1/tenants/{tenant_id}/activate/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == TenantStatus.ACTIVE

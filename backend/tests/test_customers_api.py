"""API Integration tests for Enterprise Customer Management endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestCustomerAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant Cus API",
            slug="main-tenant-cus-api",
            admin_email="owner@cusapi.com",
            admin_password="Password123!",
        )

    def test_customer_crud_and_lifecycle_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "code": "CUS-API-01",
            "customer_number": "CN-API-01",
            "customer_type": "individual",
            "first_name": "Tariq",
            "last_name": "Ziyad",
            "phone": "+967775554433",
            "email": "tariq@example.com",
        }

        # Create Customer
        response = api_client.post("/api/v1/customers/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        customer_id = data["data"]["id"]
        assert data["data"]["first_name"] == "Tariq"

        # List Customers
        list_resp = api_client.get("/api/v1/customers/", **headers)
        assert list_resp.status_code == status.HTTP_200_OK

        # Retrieve Detail
        detail_resp = api_client.get(f"/api/v1/customers/{customer_id}/", **headers)
        assert detail_resp.status_code == status.HTTP_200_OK

        # Status Lifecycle Operations
        block_resp = api_client.post(f"/api/v1/customers/{customer_id}/block/", **headers)
        assert block_resp.status_code == status.HTTP_200_OK
        assert block_resp.json()["data"]["status"] == "blocked"

        unblock_resp = api_client.post(f"/api/v1/customers/{customer_id}/unblock/", **headers)
        assert unblock_resp.status_code == status.HTTP_200_OK
        assert unblock_resp.json()["data"]["status"] == "active"

        suspend_resp = api_client.post(f"/api/v1/customers/{customer_id}/suspend/", **headers)
        assert suspend_resp.status_code == status.HTTP_200_OK
        assert suspend_resp.json()["data"]["status"] == "suspended"

        activate_resp = api_client.post(f"/api/v1/customers/{customer_id}/activate/", **headers)
        assert activate_resp.status_code == status.HTTP_200_OK
        assert activate_resp.json()["data"]["status"] == "active"

        # Fast Lookup Search
        search_resp = api_client.get("/api/v1/customers/search/?q=Tariq", **headers)
        assert search_resp.status_code == status.HTTP_200_OK
        assert len(search_resp.json()["data"]) >= 1

        # Customer Statistics
        stats_resp = api_client.get("/api/v1/customers/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        assert stats_resp.json()["data"]["total_customers"] >= 1

        # Soft Delete
        delete_resp = api_client.delete(f"/api/v1/customers/{customer_id}/", **headers)
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

"""API Integration tests for Enterprise Supplier Management endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestSupplierAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant Sup API",
            slug="main-tenant-sup-api",
            admin_email="owner@supapi.com",
            admin_password="Password123!",
        )

    def test_supplier_crud_and_lifecycle_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "code": "SUP-API-01",
            "legal_name": "API Wholesale Pharmaceuticals Ltd",
            "display_name": "API Wholesale",
            "supplier_type": "wholesaler",
            "email": "vendor@apiwholesale.com",
            "phone": "+96711122233",
            "country": "Yemen",
            "city": "Sanaa",
        }

        response = api_client.post("/api/v1/suppliers/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        supplier_id = data["data"]["id"]
        assert data["data"]["legal_name"] == "API Wholesale Pharmaceuticals Ltd"

        list_resp = api_client.get("/api/v1/suppliers/", **headers)
        assert list_resp.status_code == status.HTTP_200_OK

        suspend_resp = api_client.post(f"/api/v1/suppliers/{supplier_id}/suspend/", **headers)
        assert suspend_resp.status_code == status.HTTP_200_OK
        assert suspend_resp.json()["data"]["status"] == "suspended"

        activate_resp = api_client.post(f"/api/v1/suppliers/{supplier_id}/activate/", **headers)
        assert activate_resp.status_code == status.HTTP_200_OK
        assert activate_resp.json()["data"]["status"] == "active"

        stats_resp = api_client.get("/api/v1/suppliers/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        assert stats_resp.json()["data"]["total_suppliers"] >= 1

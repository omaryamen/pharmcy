"""API Integration tests for Enterprise Warehouse & Storage Location Management endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestWarehouseAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Main Tenant WH API",
            slug="main-tenant-wh-api",
            admin_email="owner@whapi.com",
            admin_password="Password123!",
        )
        company = Company.objects.create(tenant=tenant, code="COMP-API", legal_name="API Pharma Company")
        tenant.company = company
        return tenant

    def test_warehouse_and_location_api_flow(self, api_client, tenant_context):
        owner = tenant_context.owner
        company = tenant_context.company
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        # 1. Create Warehouse
        wh_payload = {
            "company": str(company.pk),
            "code": "WH-API-01",
            "name": "Central Pharmacy Warehouse",
            "warehouse_type": "main",
            "city": "Sanaa",
        }

        res_wh = api_client.post("/api/v1/warehouses/", data=wh_payload, format="json", **headers)
        assert res_wh.status_code == status.HTTP_201_CREATED
        wh_data = res_wh.json()["data"]
        wh_id = wh_data["id"]
        assert wh_data["name"] == "Central Pharmacy Warehouse"

        # 2. List Warehouses
        res_list = api_client.get("/api/v1/warehouses/", **headers)
        assert res_list.status_code == status.HTTP_200_OK

        # 3. Create Storage Location in Warehouse
        loc_payload = {
            "warehouse": wh_id,
            "code": "ZONE-A",
            "name": "Cold Zone",
            "location_type": "cold_room",
            "capacity": "500.00",
            "storage_conditions": ["refrigerated"],
        }
        res_loc = api_client.post(f"/api/v1/warehouses/{wh_id}/locations/", data=loc_payload, format="json", **headers)
        assert res_loc.status_code == status.HTTP_201_CREATED
        loc_data = res_loc.json()["data"]
        loc_id = loc_data["id"]
        assert loc_data["code"] == "ZONE-A"

        # 4. Get Location Tree
        res_tree = api_client.get(f"/api/v1/warehouses/{wh_id}/locations/tree/", **headers)
        assert res_tree.status_code == status.HTTP_200_OK
        tree = res_tree.json()["data"]
        assert len(tree) == 1
        assert tree[0]["code"] == "ZONE-A"

        # 5. Warehouse Stats & Search
        res_stats = api_client.get("/api/v1/warehouses/stats/", **headers)
        assert res_stats.status_code == status.HTTP_200_OK
        assert res_stats.json()["data"]["total_warehouses"] >= 1

        res_search = api_client.get("/api/v1/warehouses/search/?q=Central", **headers)
        assert res_search.status_code == status.HTTP_200_OK
        assert len(res_search.json()["data"]) >= 1

        # 6. Status transition
        res_suspend = api_client.post(f"/api/v1/warehouses/{wh_id}/suspend/", **headers)
        assert res_suspend.status_code == status.HTTP_200_OK
        assert res_suspend.json()["data"]["status"] == "suspended"

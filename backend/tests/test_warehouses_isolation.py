"""Tenant, Company, and Branch multi-tenant isolation tests for Warehouse domain."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestWarehouseTenantIsolation:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_a(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant A WH",
            slug="tenant-a-wh",
            admin_email="owner@tenanta-wh.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-A", legal_name="Company A")
        return tenant

    @pytest.fixture
    def tenant_b(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant B WH",
            slug="tenant-b-wh",
            admin_email="owner@tenantb-wh.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-B", legal_name="Company B")
        return tenant

    def test_warehouse_isolation(self, api_client, tenant_a, tenant_b):
        # Create warehouse in Tenant A
        api_client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        payload_a = {
            "company": str(tenant_a.company.pk),
            "code": "WH-TA-01",
            "name": "Tenant A Warehouse",
        }
        res_a = api_client.post("/api/v1/warehouses/", data=payload_a, format="json", **headers_a)
        assert res_a.status_code == status.HTTP_201_CREATED
        wh_a_id = res_a.json()["data"]["id"]

        # Attempt to list/retrieve Tenant A's warehouse using Tenant B credentials and headers
        api_client.force_authenticate(user=tenant_b.owner)
        headers_b = {"HTTP_X_TENANT_ID": str(tenant_b.pk)}

        res_b_list = api_client.get("/api/v1/warehouses/", **headers_b)
        assert res_b_list.status_code == status.HTTP_200_OK
        data_env = res_b_list.json()["data"]
        items = data_env["results"] if isinstance(data_env, dict) and "results" in data_env else data_env
        ids = [item["id"] for item in items]
        assert wh_a_id not in ids

        res_b_detail = api_client.get(f"/api/v1/warehouses/{wh_a_id}/", **headers_b)
        assert res_b_detail.status_code == status.HTTP_404_NOT_FOUND

"""Tenant and Company multi-tenant isolation tests for Customer domain."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestCustomerTenantIsolation:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_a(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Tenant A Customers",
            slug="tenant-a-cus",
            admin_email="owner@tenanta.com",
            admin_password="Password123!",
        )

    @pytest.fixture
    def tenant_b(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Tenant B Customers",
            slug="tenant-b-cus",
            admin_email="owner@tenantb.com",
            admin_password="Password123!",
        )

    def test_tenant_data_isolation(self, api_client, tenant_a, tenant_b):
        # Create customer in Tenant A
        api_client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        payload_a = {
            "code": "CUS-TA-01",
            "customer_number": "CN-TA-01",
            "first_name": "Tenant A Customer",
            "phone": "+967700000001",
        }
        res_a = api_client.post("/api/v1/customers/", data=payload_a, format="json", **headers_a)
        assert res_a.status_code == status.HTTP_201_CREATED
        cus_a_id = res_a.json()["data"]["id"]

        # Attempt to access Tenant A's customer using Tenant B credentials and headers
        api_client.force_authenticate(user=tenant_b.owner)
        headers_b = {"HTTP_X_TENANT_ID": str(tenant_b.pk)}

        res_b_list = api_client.get("/api/v1/customers/", **headers_b)
        assert res_b_list.status_code == status.HTTP_200_OK
        data_env = res_b_list.json()["data"]
        items = data_env["results"] if isinstance(data_env, dict) and "results" in data_env else data_env
        ids = [item["id"] for item in items]
        assert cus_a_id not in ids

        res_b_detail = api_client.get(f"/api/v1/customers/{cus_a_id}/", **headers_b)
        assert res_b_detail.status_code == status.HTTP_404_NOT_FOUND

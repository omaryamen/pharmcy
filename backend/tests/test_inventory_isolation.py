"""Tenant multi-tenant isolation tests for Inventory & Batch Management domain."""

from datetime import timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from apps.companies.models import Company
from apps.medicines.models import Medicine
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestInventoryTenantIsolation:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_a(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant A Inv",
            slug="tenant-a-inv",
            admin_email="owner@tenanta-inv.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-A", legal_name="Company A")
        return tenant

    @pytest.fixture
    def tenant_b(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant B Inv",
            slug="tenant-b-inv",
            admin_email="owner@tenantb-inv.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-B", legal_name="Company B")
        return tenant

    def test_inventory_and_batch_tenant_isolation(self, api_client, tenant_a, tenant_b):
        # Create Batch & Inventory in Tenant A
        api_client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        medicine_a = Medicine.objects.create(tenant=tenant_a, code="MED-A", sku="SKU-A", english_name="Med A", arabic_name="دواء أ")
        warehouse_a = Warehouse.objects.create(tenant=tenant_a, company=tenant_a.company, code="WH-A", name="WH A")
        loc_a = StorageLocation.objects.create(tenant=tenant_a, warehouse=warehouse_a, code="LOC-A", name="Loc A")

        exp_date = (timezone.now().date() + timedelta(days=365)).strftime("%Y-%m-%d")
        b_payload = {
            "company": str(tenant_a.company.pk),
            "medicine": str(medicine_a.pk),
            "batch_number": "BATCH-TA-01",
            "expiry_date": exp_date,
        }
        res_b_a = api_client.post("/api/v1/batches/", data=b_payload, format="json", **headers_a)
        assert res_b_a.status_code == status.HTTP_201_CREATED
        batch_a_id = res_b_a.json()["data"]["id"]

        # Attempt to access Tenant A's batch from Tenant B session
        api_client.force_authenticate(user=tenant_b.owner)
        headers_b = {"HTTP_X_TENANT_ID": str(tenant_b.pk)}

        res_b_list = api_client.get("/api/v1/batches/", **headers_b)
        assert res_b_list.status_code == status.HTTP_200_OK
        data_env = res_b_list.json()["data"]
        items = data_env["results"] if isinstance(data_env, dict) and "results" in data_env else data_env
        batch_ids = [item["id"] for item in items]
        assert batch_a_id not in batch_ids

        res_b_detail = api_client.get(f"/api/v1/batches/{batch_a_id}/", **headers_b)
        assert res_b_detail.status_code == status.HTTP_404_NOT_FOUND

"""API Integration tests for Enterprise Inventory & Batch Management endpoints."""

from datetime import timedelta
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from apps.companies.models import Company
from apps.medicines.models import Medicine
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestInventoryAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Main Tenant Inv API",
            slug="main-tenant-inv-api",
            admin_email="owner@invapi.com",
            admin_password="Password123!",
        )
        company = Company.objects.create(tenant=tenant, code="COMP-INV-API", legal_name="API Inventory Company")
        tenant.company = company
        return tenant

    def test_inventory_and_batch_api_flow(self, api_client, tenant_context):
        owner = tenant_context.owner
        company = tenant_context.company
        tenant = tenant_context
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant.pk)}

        medicine = Medicine.objects.create(
            tenant=tenant,
            code="MED-API-01",
            sku="SKU-API-01",
            english_name="Panadol Extra 500mg",
            arabic_name="بنادول إكسترا",
        )
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-API-1", name="Central WH")
        location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="LOC-A1", name="Loc A1")

        # 1. Create Batch via API
        exp_date = (timezone.now().date() + timedelta(days=300)).strftime("%Y-%m-%d")
        batch_payload = {
            "company": str(company.pk),
            "medicine": str(medicine.pk),
            "batch_number": "B-PAN-555",
            "expiry_date": exp_date,
            "unit_cost": "10.5000",
            "selling_price": "15.0000",
        }
        res_b = api_client.post("/api/v1/batches/", data=batch_payload, format="json", **headers)
        assert res_b.status_code == status.HTTP_201_CREATED
        batch_id = res_b.json()["data"]["id"]

        # 2. List Batches
        res_blist = api_client.get("/api/v1/batches/", **headers)
        assert res_blist.status_code == status.HTTP_200_OK

        # 3. Initialize Inventory Item via API
        inv_payload = {
            "company": str(company.pk),
            "warehouse": str(warehouse.pk),
            "storage_location": str(location.pk),
            "medicine": str(medicine.pk),
            "batch": batch_id,
            "unit_cost": "10.5000",
        }
        res_inv = api_client.post("/api/v1/inventory/", data=inv_payload, format="json", **headers)
        assert res_inv.status_code == status.HTTP_201_CREATED
        inv_id = res_inv.json()["data"]["id"]

        # 4. Execute Stock Adjustment (+100 units)
        adj_payload = {
            "quantity_delta": "100.00",
            "transaction_type": "receipt",
            "reason": "opening_balance",
            "reference_number": "PO-9991",
        }
        res_adj = api_client.post(f"/api/v1/inventory/{inv_id}/adjust/", data=adj_payload, format="json", **headers)
        assert res_adj.status_code == status.HTTP_200_OK
        res_data = res_adj.json()["data"]
        assert res_data["inventory_item"]["on_hand_quantity"] == "100.00"
        assert res_data["transaction"]["quantity"] == "100.00"

        # 5. Execute Stock Reservation (25 units)
        resv_payload = {"requested_quantity": "25.00", "reference_number": "SO-888"}
        res_resv = api_client.post(f"/api/v1/inventory/{inv_id}/reserve/", data=resv_payload, format="json", **headers)
        assert res_resv.status_code == status.HTTP_200_OK
        assert res_resv.json()["data"]["inventory_item"]["reserved_quantity"] == "25.00"
        assert res_resv.json()["data"]["inventory_item"]["available_quantity"] == "75.00"

        # 6. Check Inventory Summary
        res_sum = api_client.get("/api/v1/inventory/summary/", **headers)
        assert res_sum.status_code == status.HTTP_200_OK
        assert Decimal(str(res_sum.json()["data"]["total_on_hand"])) == Decimal("100.00")

        # 7. Check FEFO Lookup Endpoint
        res_fefo = api_client.get(f"/api/v1/batches/fefo/?medicine={medicine.pk}", **headers)
        assert res_fefo.status_code == status.HTTP_200_OK
        assert len(res_fefo.json()["data"]) >= 1

        # 8. Check Transactions List
        res_tx = api_client.get("/api/v1/inventory-transactions/", **headers)
        assert res_tx.status_code == status.HTTP_200_OK

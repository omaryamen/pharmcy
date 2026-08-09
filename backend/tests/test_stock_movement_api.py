"""API Integration tests for Stock Movement Engine REST endpoints."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.medicines.models import Medicine
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant SM API",
            slug="tenant-sm-api",
            admin_email="owner@smapi.com",
            admin_password="Password123!",
        )
        company = Company.objects.create(tenant=tenant, code="C-SM-API", legal_name="SM API Company")
        tenant.company = company
        return tenant

    def test_stock_movement_api_flow(self, api_client, tenant_context):
        tenant = tenant_context
        owner = tenant.owner
        company = tenant.company
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant.pk)}

        medicine = Medicine.objects.create(tenant=tenant, code="MED-SM-API", sku="SKU-SM-API", english_name="Augmentin 1g", arabic_name="أوجمنتين")
        src_wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-A", name="Warehouse A")
        dst_wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-B", name="Warehouse B")
        src_loc = StorageLocation.objects.create(tenant=tenant, warehouse=src_wh, code="LOC-A1", name="Loc A1")
        dst_loc = StorageLocation.objects.create(tenant=tenant, warehouse=dst_wh, code="LOC-B1", name="Loc B1")

        # 1. Stock Receive Endpoint
        rec_payload = {
            "company": str(company.pk),
            "warehouse": str(src_wh.pk),
            "location": str(src_loc.pk),
            "medicine": str(medicine.pk),
            "quantity": "200.00",
            "unit_cost": "15.0000",
            "reference_number": "GRN-99001",
        }
        res_rec = api_client.post("/api/v1/stock-movements/receive/", data=rec_payload, format="json", **headers)
        assert res_rec.status_code == status.HTTP_201_CREATED
        res_data = res_rec.json()["data"]
        rec_id = res_data.get("id") or res_data.get("data", {}).get("id")

        # 2. Stock Transfer Endpoint
        trf_payload = {
            "company": str(company.pk),
            "source_warehouse": str(src_wh.pk),
            "destination_warehouse": str(dst_wh.pk),
            "source_location": str(src_loc.pk),
            "destination_location": str(dst_loc.pk),
            "medicine": str(medicine.pk),
            "quantity": "50.00",
            "reference_number": "TRF-77001",
        }
        res_trf = api_client.post("/api/v1/stock-movements/transfer/", data=trf_payload, format="json", **headers)
        assert res_trf.status_code == status.HTTP_201_CREATED
        trf_data = res_trf.json()["data"]
        trf_id = trf_data.get("id") or trf_data.get("data", {}).get("id")

        # 3. Stock Reverse Endpoint (Reverse the Transfer)
        res_rev = api_client.post(f"/api/v1/stock-movements/{trf_id}/reverse/", data={"reason": "Error correction"}, format="json", **headers)
        rev_data = res_rev.json()["data"]
        is_rev = rev_data.get("is_reversal") if "is_reversal" in rev_data else rev_data.get("data", {}).get("is_reversal")
        assert is_rev is True

        # 4. Movement List Endpoint
        res_list = api_client.get("/api/v1/stock-movements/", **headers)
        assert res_list.status_code == status.HTTP_200_OK

        # 5. Statistics Endpoint
        res_stats = api_client.get("/api/v1/stock-movements/stats/", **headers)
        assert res_stats.status_code == status.HTTP_200_OK

        # 6. Traceability Endpoint
        res_trace = api_client.get(f"/api/v1/stock-movements/traceability/?medicine={medicine.pk}", **headers)
        assert res_trace.status_code == status.HTTP_200_OK

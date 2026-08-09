"""Multi-tenant isolation tests for Stock Movement Engine."""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.medicines.models import Medicine
from apps.stock_movement.services import StockMovementEngine
from apps.tenants.services import TenantProvisioningService
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementTenantIsolation:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_a(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant A SM",
            slug="tenant-a-sm",
            admin_email="owner@tenanta-sm.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-A-SM", legal_name="Company A SM")
        return tenant

    @pytest.fixture
    def tenant_b(self):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Tenant B SM",
            slug="tenant-b-sm",
            admin_email="owner@tenantb-sm.com",
            admin_password="Password123!",
        )
        tenant.company = Company.objects.create(tenant=tenant, code="C-B-SM", legal_name="Company B SM")
        return tenant

    def test_stock_movement_tenant_isolation(self, api_client, tenant_a, tenant_b):
        # Create Movement in Tenant A
        api_client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        med_a = Medicine.objects.create(tenant=tenant_a, code="MED-A", sku="SKU-A", english_name="Med A", arabic_name="دواء أ")
        wh_a = Warehouse.objects.create(tenant=tenant_a, company=tenant_a.company, code="WH-A", name="WH A")
        loc_a = StorageLocation.objects.create(tenant=tenant_a, warehouse=wh_a, code="LOC-A", name="Loc A")

        engine = StockMovementEngine()
        mov_a = engine.receive_stock(tenant=tenant_a, company=tenant_a.company, warehouse=wh_a, location=loc_a, medicine=med_a, quantity=Decimal("100.00"))

        # Tenant B attempts to view or reverse Tenant A's stock movement
        api_client.force_authenticate(user=tenant_b.owner)
        headers_b = {"HTTP_X_TENANT_ID": str(tenant_b.pk)}

        res_list = api_client.get("/api/v1/stock-movements/", **headers_b)
        assert res_list.status_code == status.HTTP_200_OK
        data_env = res_list.json()["data"]
        items = data_env["results"] if isinstance(data_env, dict) and "results" in data_env else data_env
        mov_ids = [m["id"] for m in items]
        assert str(mov_a.pk) not in mov_ids

        res_detail = api_client.get(f"/api/v1/stock-movements/{mov_a.pk}/", **headers_b)
        assert res_detail.status_code == status.HTTP_404_NOT_FOUND

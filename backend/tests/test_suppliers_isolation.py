"""Tests verifying cross-tenant supplier data isolation."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.suppliers.services import SupplierService
from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestSupplierIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def service(self):
        return SupplierService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha SUP", slug="tenant-alpha-sup", admin_email="owner_a@alphasup.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta SUP", slug="tenant-beta-sup", admin_email="owner_b@betasup.com")

    def test_tenant_cannot_access_other_tenant_suppliers(self, tenant_a, tenant_b, service):
        sup_a = service.create_supplier(tenant=tenant_a, code="SUP-A", legal_name="Supplier A Legal")
        sup_b = service.create_supplier(tenant=tenant_b, code="SUP-B", legal_name="Supplier B Legal")

        client = APIClient()
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/suppliers/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        codes = [item["code"] for item in data["data"]["results"]]

        assert sup_a.code in codes
        assert sup_b.code not in codes

        detail_resp = client.get(f"/api/v1/suppliers/{sup_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

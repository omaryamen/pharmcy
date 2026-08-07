"""Tests verifying cross-tenant reference data isolation."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.references.services import ReferenceDataService
from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestReferenceIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def service(self):
        return ReferenceDataService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha REF", slug="tenant-alpha-ref", admin_email="owner_a@alpharef.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta REF", slug="tenant-beta-ref", admin_email="owner_b@betaref.com")

    def test_tenant_cannot_access_other_tenant_categories(self, tenant_a, tenant_b, service):
        cat_a = service.create_category(tenant=tenant_a, code="CAT-A", name_en="Category A", name_ar="فئة أ")
        cat_b = service.create_category(tenant=tenant_b, code="CAT-B", name_en="Category B", name_ar="فئة ب")

        client = APIClient()
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/references/categories/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        codes = [item["code"] for item in data["data"]["results"]]

        assert cat_a.code in codes
        assert cat_b.code not in codes

        detail_resp = client.get(f"/api/v1/references/categories/{cat_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

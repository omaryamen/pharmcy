"""Tests verifying cross-tenant and cross-company medicine data isolation."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.services import CompanyService
from apps.medicines.services import MedicineService
from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestMedicineIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def company_service(self):
        return CompanyService()

    @pytest.fixture
    def medicine_service(self):
        return MedicineService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Alpha MED", slug="tenant-alpha-med", admin_email="owner_a@alphamed.com")

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(name="Tenant Beta MED", slug="tenant-beta-med", admin_email="owner_b@betamed.com")

    def test_tenant_cannot_access_other_tenant_medicines(self, tenant_a, tenant_b, company_service, medicine_service):
        comp_a = company_service.create_company(tenant=tenant_a, legal_name="Co Alpha Med", code="co_alpha_m", slug="co-alpha-m")
        comp_b = company_service.create_company(tenant=tenant_b, legal_name="Co Beta Med", code="co_beta_m", slug="co-beta-m")

        med_a = medicine_service.create_medicine(
            tenant=tenant_a, company=comp_a, code="MED-ALPHA-1", sku="SKU-A1", arabic_name="دواء أ", english_name="Med Alpha 1"
        )
        med_b = medicine_service.create_medicine(
            tenant=tenant_b, company=comp_b, code="MED-BETA-1", sku="SKU-B1", arabic_name="دواء ب", english_name="Med Beta 1"
        )

        client = APIClient()
        client.force_authenticate(user=tenant_a.owner)
        headers_a = {"HTTP_X_TENANT_ID": str(tenant_a.pk)}

        response = client.get("/api/v1/medicines/", **headers_a)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        ids = [item["id"] for item in data["data"]["results"]]

        assert str(med_a.pk) in ids
        assert str(med_b.pk) not in ids

        detail_resp = client.get(f"/api/v1/medicines/{med_b.pk}/", **headers_a)
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_same_medicine_code_allowed_in_different_tenants(self, tenant_a, tenant_b, medicine_service):
        med_a = medicine_service.create_medicine(
            tenant=tenant_a, code="COMMON-CODE", sku="SKU-COM-A", arabic_name="مشترك أ", english_name="Common A"
        )
        med_b = medicine_service.create_medicine(
            tenant=tenant_b, code="COMMON-CODE", sku="SKU-COM-B", arabic_name="مشترك ب", english_name="Common B"
        )

        assert med_a.pk != med_b.pk
        assert med_a.tenant == tenant_a
        assert med_b.tenant == tenant_b

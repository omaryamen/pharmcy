"""API Integration tests for Enterprise Medicine Master Data endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.services import CompanyService
from apps.medicines.services import MedicineService
from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestMedicineAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant Med API",
            slug="main-tenant-med-api",
            admin_email="owner@medapi.com",
            admin_password="Password123!",
        )

    @pytest.fixture
    def company(self, tenant_context):
        return CompanyService().create_company(
            tenant=tenant_context,
            legal_name="Pharma Dist Corp",
            code="pharma_dist",
            slug="pharma-dist",
        )

    def test_create_and_list_medicines_api(self, api_client, tenant_context, company):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {
            "company": str(company.pk),
            "code": "API-MED-01",
            "sku": "API-SKU-01",
            "barcode": "1122334455667",
            "arabic_name": "أسبرين 100 ملجم",
            "english_name": "Aspirin 100mg",
            "dosage_form": "Tablet",
            "default_purchase_price": 50.00,
            "default_selling_price": 75.00,
        }

        response = api_client.post("/api/v1/medicines/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["english_name"] == "Aspirin 100mg"

        list_response = api_client.get("/api/v1/medicines/?search=Aspirin", **headers)
        assert list_response.status_code == status.HTTP_200_OK
        list_data = list_response.json()
        assert len(list_data["data"]["results"]) >= 1

    def test_barcode_lookup_and_stats_api(self, api_client, tenant_context, company):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        medicine = MedicineService().create_medicine(
            tenant=tenant_context,
            company=company,
            code="API-MED-02",
            sku="API-SKU-02",
            barcode="9988776655443",
            arabic_name="فولتارين 50 ملجم",
            english_name="Voltaren 50mg",
        )

        lookup_resp = api_client.get("/api/v1/medicines/lookup/barcode/?barcode=9988776655443", **headers)
        assert lookup_resp.status_code == status.HTTP_200_OK
        lookup_data = lookup_resp.json()
        assert lookup_data["data"]["id"] == str(medicine.pk)

        stats_resp = api_client.get("/api/v1/medicines/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        stats_data = stats_resp.json()
        assert stats_data["data"]["total_medicines"] >= 1

"""API Integration tests for Enterprise Pharmaceutical Reference Data endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.references.services import ReferenceDataService
from apps.tenants.services import TenantProvisioningService


@pytest.mark.django_db
class TestReferenceAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def tenant_context(self):
        provisioner = TenantProvisioningService()
        return provisioner.provision_tenant(
            name="Main Tenant Ref API",
            slug="main-tenant-ref-api",
            admin_email="owner@refapi.com",
            admin_password="Password123!",
        )

    def test_category_and_manufacturer_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        payload = {"code": "CARDIO", "name_en": "Cardiology", "name_ar": "أدوية القلب"}
        response = api_client.post("/api/v1/references/categories/", data=payload, format="json", **headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["data"]["name_en"] == "Cardiology"

        tree_resp = api_client.get("/api/v1/references/categories/tree/", **headers)
        assert tree_resp.status_code == status.HTTP_200_OK

        mfr_payload = {"code": "PFIZER", "legal_name": "Pfizer Inc", "display_name": "Pfizer", "country_of_origin": "USA"}
        mfr_resp = api_client.post("/api/v1/references/manufacturers/", data=mfr_payload, format="json", **headers)
        assert mfr_resp.status_code == status.HTTP_201_CREATED

    def test_seed_and_stats_api(self, api_client, tenant_context):
        owner = tenant_context.owner
        api_client.force_authenticate(user=owner)
        headers = {"HTTP_X_TENANT_ID": str(tenant_context.pk)}

        seed_resp = api_client.post("/api/v1/references/seed/", **headers)
        assert seed_resp.status_code == status.HTTP_200_OK

        stats_resp = api_client.get("/api/v1/references/stats/", **headers)
        assert stats_resp.status_code == status.HTTP_200_OK
        stats_data = stats_resp.json()
        assert stats_data["data"]["dosage_forms_count"] >= 1

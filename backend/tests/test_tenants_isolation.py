"""Tests verifying tenant data isolation and host resolution."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.common.utils.tenant import resolve_tenant
from apps.tenants.services import TenantProvisioningService

User = get_user_model()


@pytest.mark.django_db
class TestTenantIsolation:
    @pytest.fixture
    def provisioner(self):
        return TenantProvisioningService()

    @pytest.fixture
    def tenant_a(self, provisioner):
        return provisioner.provision_tenant(
            name="Pharmacy A", slug="pharmacy-a", admin_email="owner_a@pharmacy-a.com"
        )

    @pytest.fixture
    def tenant_b(self, provisioner):
        return provisioner.provision_tenant(
            name="Pharmacy B", slug="pharmacy-b", admin_email="owner_b@pharmacy-b.com"
        )

    def test_tenant_resolution_via_header(self, tenant_a):
        class MockRequest:
            headers = {"X-Tenant-Slug": "pharmacy-a"}

            def get_host(self):
                return "localhost"

        resolved = resolve_tenant(MockRequest())
        assert resolved == tenant_a

    def test_tenant_resolution_via_subdomain_host(self, tenant_b):
        class MockRequest:
            headers = {}

            def get_host(self):
                return "pharmacy-b.pharmacloud.local:8000"

        resolved = resolve_tenant(MockRequest())
        assert resolved == tenant_b

    def test_cross_tenant_access_denied(self, tenant_a, tenant_b):
        client = APIClient()

        # Authenticate as Owner A
        client.force_authenticate(user=tenant_a.owner)

        # Attempt to request Tenant B profile using Tenant B header
        headers = {"HTTP_X_TENANT_ID": str(tenant_b.pk)}
        response = client.get("/api/v1/tenants/me/profile/", **headers)

        # Permission IsTenantMember / CanManageTenantSettings blocks Owner A from accessing Tenant B
        assert response.status_code in {status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED}

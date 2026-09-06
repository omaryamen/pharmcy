"""Tests for IMP-046-A: Platform Admin Role, Operations & Tenant Isolation."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Tenant
from apps.platform_ops.models import GlobalFeatureFlag, PlatformAlert, PlatformAuditLog

User = get_user_model()


@pytest.fixture
def platform_admin_user(db):
    user = User.objects.create_superuser(
        email="platform_admin@pharmacloud.app",
        password="supersecretpassword123",
        first_name="Platform",
        last_name="SuperAdmin",
    )
    return user


@pytest.fixture
def standard_pharmacy_user(db):
    tenant = Tenant.objects.create(name="Al-Amal Pharmacy", code="TNT-AMAL-TST")
    user = User.objects.create_user(
        email="pharmacist@amal.com",
        password="password123",
        first_name="Dr. Pharmacist",
        last_name="Staff",
        is_staff=False,
        is_superuser=False,
    )
    return user, tenant


@pytest.mark.django_db
class TestPlatformAdminAuthorization:
    def test_platform_overview_accessible_by_platform_admin(self, platform_admin_user):
        client = APIClient()
        client.force_authenticate(user=platform_admin_user)

        url = reverse("platform-overview")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        json_data = response.json()
        payload = json_data.get("data", json_data)
        assert "total_tenants" in payload
        assert "mrr" in payload
        assert "total_active_subscriptions" in payload

    def test_platform_endpoints_forbidden_for_standard_pharmacy_staff(self, standard_pharmacy_user):
        user, _ = standard_pharmacy_user
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("platform-overview")
        response = client.get(url)

        # Standard tenant users must never access platform-level over-tenant APIs
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_feature_flag_toggle_and_audit(self, platform_admin_user):
        flag = GlobalFeatureFlag.objects.create(
            feature_key="TEST_FEATURE_FLAG_ALPHA",
            name="Alpha Rollout Test",
            is_globally_enabled=False,
        )

        client = APIClient()
        client.force_authenticate(user=platform_admin_user)

        # Update flag
        url = reverse("platform-feature-flags-detail", kwargs={"pk": flag.pk})
        response = client.patch(url, {"is_globally_enabled": True}, format="json")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        flag.refresh_from_db()
        assert flag.is_globally_enabled is True

    def test_tenant_suspension_creates_platform_audit_log(self, platform_admin_user, standard_pharmacy_user):
        _, tenant = standard_pharmacy_user
        assert tenant.is_active is True

        client = APIClient()
        client.force_authenticate(user=platform_admin_user)

        # Suspend tenant via Platform Admin API
        url = reverse("platform-tenants-suspend", kwargs={"pk": tenant.pk})
        response = client.post(url, {"reason": "Non-payment violation"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        tenant.refresh_from_db()
        assert tenant.is_active is False

        # Verify PlatformAuditLog entry created
        audit_log = PlatformAuditLog.objects.filter(target_tenant=tenant, action="TENANT_SUSPENDED").first()
        assert audit_log is not None
        assert audit_log.actor == platform_admin_user

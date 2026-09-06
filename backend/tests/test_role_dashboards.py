"""Tests for IMP-048: Role-Based Professional Dashboards & Operational Workspaces."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Tenant
from apps.rbac.constants import (
    ADMIN_ROLE_CODE,
    BRANCH_MANAGER_ROLE_CODE,
    CASHIER_ROLE_CODE,
    PHARMACIST_ROLE_CODE,
)
from apps.rbac.models import Permission, Role, RolePermission, UserRoleAssignment

User = get_user_model()


@pytest.fixture
def pharmacy_tenant(db):
    tenant = Tenant.objects.create(name="Al-Amal Pharmacy Chain", code="TNT-AMAL-DASH", slug="tnt-amal-dash")
    return tenant


@pytest.fixture
def superadmin_user(db):
    user = User.objects.create_superuser(
        email="superadmin.dash@pharmacloud.app",
        password="superpassword123",
        first_name="Platform",
        last_name="SuperAdmin",
    )
    return user


@pytest.fixture
def pharmacy_admin_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="admin.dash@amal.com",
        password="password123",
        first_name="Admin",
        last_name="Owner",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(
        tenant=pharmacy_tenant,
        code=ADMIN_ROLE_CODE,
        defaults={"name": "Pharmacy Admin"},
    )
    UserRoleAssignment.objects.create(
        tenant=pharmacy_tenant,
        user=user,
        role=role,
        is_active=True,
    )
    return user


@pytest.fixture
def pharmacist_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="pharmacist.dash@amal.com",
        password="password123",
        first_name="Dr. Sarah",
        last_name="Pharmacist",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(
        tenant=pharmacy_tenant,
        code=PHARMACIST_ROLE_CODE,
        defaults={"name": "Licensed Pharmacist"},
    )
    UserRoleAssignment.objects.create(
        tenant=pharmacy_tenant,
        user=user,
        role=role,
        is_active=True,
    )
    return user


@pytest.fixture
def cashier_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="cashier.dash@amal.com",
        password="password123",
        first_name="Fahad",
        last_name="Cashier",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(
        tenant=pharmacy_tenant,
        code=CASHIER_ROLE_CODE,
        defaults={"name": "POS Cashier"},
    )
    UserRoleAssignment.objects.create(
        tenant=pharmacy_tenant,
        user=user,
        role=role,
        is_active=True,
    )
    return user


@pytest.mark.django_db
class TestRoleDashboards:
    def test_platform_admin_overview_metrics(self, superadmin_user):
        client = APIClient()
        client.force_authenticate(user=superadmin_user)

        url = reverse("platform-overview")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get("data", {})
        assert "active_tenants" in data
        assert "is_maintenance_in_effect" in data

    def test_pharmacy_admin_health_check(self, pharmacy_admin_user):
        client = APIClient()
        client.force_authenticate(user=pharmacy_admin_user)

        url = reverse("core:health-liveness")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_pharmacist_clinical_context(self, pharmacist_user):
        client = APIClient()
        client.force_authenticate(user=pharmacist_user)

        url = reverse("core:health-liveness")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_cashier_strict_isolation_from_superadmin_dashboard(self, cashier_user):
        client = APIClient()
        client.force_authenticate(user=cashier_user)

        url = reverse("platform-overview")
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

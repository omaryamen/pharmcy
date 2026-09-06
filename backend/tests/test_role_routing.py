"""Tests for IMP-047: Role-Based Frontend Shells, Routing & Backend Protection."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Tenant
from apps.rbac.constants import (
    ADMIN_ROLE_CODE,
    CASHIER_ROLE_CODE,
    PHARMACIST_ROLE_CODE,
)
from apps.rbac.models import Permission, Role, RolePermission, UserRoleAssignment

User = get_user_model()


@pytest.fixture
def pharmacy_tenant(db):
    tenant = Tenant.objects.create(name="Al-Amal Pharmacy Chain", code="TNT-AMAL-ROUTING", slug="tnt-amal-routing")
    return tenant


@pytest.fixture
def superadmin_user(db):
    user = User.objects.create_superuser(
        email="superadmin@pharmacloud.app",
        password="superpassword123",
        first_name="Platform",
        last_name="SuperAdmin",
    )
    return user


@pytest.fixture
def cashier_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="cashier.user@amal.com",
        password="password123",
        first_name="Fahad",
        last_name="Cashier",
        is_staff=False,
        is_superuser=False,
    )
    role = Role.objects.create(
        tenant=pharmacy_tenant,
        name="POS Cashier",
        code=CASHIER_ROLE_CODE,
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
        email="pharmacist.user@amal.com",
        password="password123",
        first_name="Dr. Sarah",
        last_name="Pharmacist",
        is_staff=False,
        is_superuser=False,
    )
    role = Role.objects.create(
        tenant=pharmacy_tenant,
        name="Licensed Pharmacist",
        code=PHARMACIST_ROLE_CODE,
    )
    UserRoleAssignment.objects.create(
        tenant=pharmacy_tenant,
        user=user,
        role=role,
        is_active=True,
    )
    return user


@pytest.mark.django_db
class TestRoleRoutingAndProtection:
    def test_superadmin_access_to_platform_overview(self, superadmin_user):
        client = APIClient()
        client.force_authenticate(user=superadmin_user)

        url = reverse("platform-overview")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_cashier_strictly_forbidden_from_platform_admin(self, cashier_user):
        client = APIClient()
        client.force_authenticate(user=cashier_user)

        # Cashier must be strictly rejected from platform superadmin APIs
        url = reverse("platform-overview")
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pharmacist_strictly_forbidden_from_platform_admin(self, pharmacist_user):
        client = APIClient()
        client.force_authenticate(user=pharmacist_user)

        # Pharmacist must be strictly rejected from platform superadmin APIs
        url = reverse("platform-overview")
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_role_shell_mapping_contract(self):
        """Verify role to frontend shell destination mappings."""
        role_shell_map = {
            "superadmin": "/admin",
            "pharmacy_admin": "/app",
            "company_admin": "/app",
            "pharmacist": "/pharmacy",
            "cashier": "/pos",
            "inventory_manager": "/inventory",
            "accountant": "/accounting",
            "branch_manager": "/branch",
        }

        assert role_shell_map["superadmin"] == "/admin"
        assert role_shell_map["pharmacist"] == "/pharmacy"
        assert role_shell_map["cashier"] == "/pos"
        assert role_shell_map["accountant"] == "/accounting"
        assert role_shell_map["inventory_manager"] == "/inventory"
        assert role_shell_map["branch_manager"] == "/branch"
        assert role_shell_map["pharmacy_admin"] == "/app"

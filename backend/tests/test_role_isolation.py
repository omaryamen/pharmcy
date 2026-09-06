"""Tests for IMP-050: Deep Role Isolation, Routing & Workspace Logic Audit."""

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
    COMPANY_ADMIN_ROLE_CODE,
    CUSTOMER_SERVICE_ROLE_CODE,
    INVENTORY_MANAGER_ROLE_CODE,
    ACCOUNTANT_ROLE_CODE,
    PHARMACIST_ROLE_CODE,
    PURCHASING_OFFICER_ROLE_CODE,
    SALES_SUPERVISOR_ROLE_CODE,
    PREDEFINED_STAFF_ROLES,
)
from apps.rbac.models import Permission, Role, RolePermission, UserRoleAssignment

User = get_user_model()


@pytest.fixture
def tenant_alpha(db):
    return Tenant.objects.create(name="Alpha Pharmacy Chain", code="TNT-ALPHA-050", slug="tnt-alpha-050")


@pytest.fixture
def tenant_beta(db):
    return Tenant.objects.create(name="Beta Pharmacy Chain", code="TNT-BETA-050", slug="tnt-beta-050")


@pytest.fixture
def superadmin_user(db):
    return User.objects.create_superuser(
        email="superadmin.050@pharmacloud.app",
        password="password123",
        first_name="Platform",
        last_name="SuperAdmin",
    )


@pytest.fixture
def pharmacist_alpha(db, tenant_alpha):
    user = User.objects.create_user(
        email="pharmacist.alpha@alpha.com",
        password="password123",
        first_name="Dr. Sarah",
        last_name="Pharmacist",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(tenant=tenant_alpha, code=PHARMACIST_ROLE_CODE, defaults={"name": "Pharmacist"})
    UserRoleAssignment.objects.create(tenant=tenant_alpha, user=user, role=role, is_active=True)
    return user


@pytest.fixture
def cashier_alpha(db, tenant_alpha):
    user = User.objects.create_user(
        email="cashier.alpha@alpha.com",
        password="password123",
        first_name="Fahad",
        last_name="Cashier",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(tenant=tenant_alpha, code=CASHIER_ROLE_CODE, defaults={"name": "Cashier"})
    UserRoleAssignment.objects.create(tenant=tenant_alpha, user=user, role=role, is_active=True)
    return user


@pytest.fixture
def accountant_alpha(db, tenant_alpha):
    user = User.objects.create_user(
        email="accountant.alpha@alpha.com",
        password="password123",
        first_name="Tariq",
        last_name="Accountant",
        is_staff=False,
    )
    role, _ = Role.objects.get_or_create(tenant=tenant_alpha, code=ACCOUNTANT_ROLE_CODE, defaults={"name": "Accountant"})
    UserRoleAssignment.objects.create(tenant=tenant_alpha, user=user, role=role, is_active=True)
    return user


@pytest.mark.django_db
class TestDeepRoleIsolation:
    def test_complete_roles_catalog_coverage(self):
        """Assert all 10 predefined roles exist in standard configuration."""
        codes = [r["code"] for r in PREDEFINED_STAFF_ROLES]
        expected_roles = [
            ADMIN_ROLE_CODE,
            COMPANY_ADMIN_ROLE_CODE,
            BRANCH_MANAGER_ROLE_CODE,
            PHARMACIST_ROLE_CODE,
            CASHIER_ROLE_CODE,
            INVENTORY_MANAGER_ROLE_CODE,
            ACCOUNTANT_ROLE_CODE,
            PURCHASING_OFFICER_ROLE_CODE,
            SALES_SUPERVISOR_ROLE_CODE,
            CUSTOMER_SERVICE_ROLE_CODE,
        ]
        for role_code in expected_roles:
            assert role_code in codes

    def test_platform_superadmin_exclusive_access(self, superadmin_user, pharmacist_alpha, cashier_alpha):
        """Superadmin can access platform operations; staff roles are strictly forbidden (403)."""
        client = APIClient()

        # SuperAdmin -> 200 OK
        client.force_authenticate(user=superadmin_user)
        res_super = client.get(reverse("platform-overview"))
        assert res_super.status_code == status.HTTP_200_OK

        # Pharmacist -> 403 Forbidden
        client.force_authenticate(user=pharmacist_alpha)
        res_pharm = client.get(reverse("platform-overview"))
        assert res_pharm.status_code == status.HTTP_403_FORBIDDEN

        # Cashier -> 403 Forbidden
        client.force_authenticate(user=cashier_alpha)
        res_cash = client.get(reverse("platform-overview"))
        assert res_cash.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_tenant_isolation_boundary(self, tenant_alpha, tenant_beta, pharmacist_alpha):
        """Tenant Alpha pharmacist cannot mutate Tenant Beta roles or assets."""
        client = APIClient()
        client.force_authenticate(user=pharmacist_alpha)

        # Attempt to create a role inside Tenant Beta -> Must be forbidden / unpermitted
        beta_role_url = f"/api/v1/tenants/{tenant_beta.id}/roles/"
        res = client.post(beta_role_url, {"name": "Hacked Role", "code": "hacked"}, format="json")
        assert res.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_privilege_escalation_denied(self, cashier_alpha, tenant_alpha):
        """Cashier attempting to self-assign Admin role or modify permissions is rejected."""
        client = APIClient()
        client.force_authenticate(user=cashier_alpha)

        admin_role, _ = Role.objects.get_or_create(
            tenant=tenant_alpha,
            code=ADMIN_ROLE_CODE,
            defaults={"name": "Pharmacy Admin"},
        )

        escalate_url = f"/api/v1/users/{cashier_alpha.id}/roles/"
        res = client.post(escalate_url, {"role_id": str(admin_role.id)}, format="json")
        assert res.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

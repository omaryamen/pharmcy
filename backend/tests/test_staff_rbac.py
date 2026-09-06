"""Tests for IMP-046-C: Enterprise Pharmacy Staff, Roles, Permissions & Scopes."""

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
    PREDEFINED_STAFF_ROLES,
)
from apps.rbac.models import Permission, Role, RolePermission, UserRoleAssignment

User = get_user_model()


@pytest.fixture
def pharmacy_tenant(db):
    tenant = Tenant.objects.create(name="Al-Amal Pharmacy Chain", code="TNT-AMAL-STAFF", slug="tnt-amal-staff")
    return tenant


@pytest.fixture
def pharmacist_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="pharmacist.sarah@amal.com",
        password="password123",
        first_name="Dr. Sarah",
        last_name="Al-Ghamdi",
    )
    return user


@pytest.fixture
def cashier_user(db, pharmacy_tenant):
    user = User.objects.create_user(
        email="cashier.fahad@amal.com",
        password="password123",
        first_name="Fahad",
        last_name="Al-Harbi",
    )
    return user


@pytest.mark.django_db
class TestStaffRolesAndPermissions:
    def test_predefined_staff_roles_catalog(self):
        codes = [r["code"] for r in PREDEFINED_STAFF_ROLES]
        assert ADMIN_ROLE_CODE in codes
        assert PHARMACIST_ROLE_CODE in codes
        assert CASHIER_ROLE_CODE in codes
        assert BRANCH_MANAGER_ROLE_CODE in codes

    def test_custom_role_creation(self, pharmacy_tenant):
        custom_role = Role.objects.create(
            tenant=pharmacy_tenant,
            name="Senior Night Shift Dispenser",
            code="senior_night_dispenser",
            description="Custom staff role with emergency dispensing permissions",
            is_protected=False,
        )
        assert custom_role.pk is not None
        assert custom_role.tenant == pharmacy_tenant
        assert custom_role.code == "senior_night_dispenser"

    def test_role_assignment_to_staff_user(self, pharmacy_tenant, pharmacist_user):
        role = Role.objects.create(
            tenant=pharmacy_tenant,
            name="Licensed Pharmacist",
            code=PHARMACIST_ROLE_CODE,
        )

        assignment = UserRoleAssignment.objects.create(
            tenant=pharmacy_tenant,
            user=pharmacist_user,
            role=role,
            is_primary=True,
            is_active=True,
        )

        assert assignment.user == pharmacist_user
        assert assignment.role == role
        assert assignment.tenant == pharmacy_tenant
        assert assignment.is_active is True

    def test_role_permission_grant_and_denial(self, pharmacy_tenant):
        role = Role.objects.create(
            tenant=pharmacy_tenant,
            name="POS Cashier",
            code=CASHIER_ROLE_CODE,
        )
        perm_pos, _ = Permission.objects.get_or_create(
            code="pos.manage",
            defaults={
                "name": "Manage Point of Sale",
                "module": "pos",
                "category": "general",
                "action": "manage",
                "scope": "tenant",
            },
        )
        perm_gl, _ = Permission.objects.get_or_create(
            code="gl.manage",
            defaults={
                "name": "Manage General Ledger",
                "module": "gl",
                "category": "general",
                "action": "manage",
                "scope": "tenant",
            },
        )

        # Cashier is granted POS and explicitly denied GL
        link_pos = RolePermission.objects.create(role=role, permission=perm_pos, allow=True)
        link_gl = RolePermission.objects.create(role=role, permission=perm_gl, allow=False)

        assert link_pos.allow is True
        assert link_gl.allow is False

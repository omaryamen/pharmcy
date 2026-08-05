"""Model-level tests for the RBAC app: catalog seeding, constraints, tenancy, soft delete."""

from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.rbac.constants import PERMISSION_CATALOG
from apps.rbac.models import (
    Permission,
    PermissionScope,
    Role,
    RoleGroup,
    RoleGroupMembership,
    RoleHierarchy,
    RolePermission,
    RoleVersion,
    UserPermissionOverride,
    UserRoleAssignment,
)
from tests.factories import (
    PermissionFactory,
    RoleFactory,
    RoleGroupFactory,
    TenantFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


class TestPermissionCatalog:
    def test_catalog_is_seeded_by_migration(self):
        assert Permission.objects.count() == len(PERMISSION_CATALOG)

    def test_all_seeded_permissions_are_system_and_active(self):
        assert Permission.objects.filter(is_system=True).count() == len(PERMISSION_CATALOG)
        assert Permission.objects.filter(is_active=False).count() == 0

    def test_catalog_codes_are_unique(self):
        distinct = Permission.objects.values_list("code", flat=True).distinct().count()
        assert distinct == Permission.objects.count()

    def test_catalog_matches_constants_snapshot(self):
        db_codes = set(Permission.objects.values_list("code", flat=True))
        assert db_codes == {entry["code"] for entry in PERMISSION_CATALOG}

    def test_platform_permissions_are_platform_scope(self):
        platform = Permission.objects.get(code="platform.manage")
        assert platform.scope == PermissionScope.PLATFORM

    def test_tenant_permissions_are_tenant_scope(self):
        assert Permission.objects.get(code="catalog.item.read").scope == PermissionScope.TENANT

    def test_custom_permission_defaults(self):
        permission = PermissionFactory()
        assert permission.is_system is False
        assert permission.is_active is True
        assert permission.scope == PermissionScope.TENANT


class TestRoleModel:
    def test_bootstrap_provisions_admin_and_member(self, tenant):
        codes = set(Role.objects.filter(tenant=tenant).values_list("code", flat=True))
        assert {"admin", "member"} <= codes
        admin = Role.objects.get(tenant=tenant, code="admin")
        assert admin.is_protected is True
        member = Role.objects.get(tenant=tenant, code="member")
        assert member.is_default is True
        assert member.is_protected is False

    def test_admin_role_grants_every_tenant_permission(self, tenant):
        admin = Role.objects.get(tenant=tenant, code="admin")
        granted = set(admin.permission_links.values_list("permission__code", flat=True))
        expected = set(Permission.objects.filter(scope=PermissionScope.TENANT).values_list("code", flat=True))
        assert granted == expected

    def test_member_role_grants_only_read_permissions(self, tenant):
        member = Role.objects.get(tenant=tenant, code="member")
        granted = set(member.permission_links.values_list("permission__code", flat=True))
        assert granted
        assert all(code.endswith(".read") for code in granted)

    def test_role_code_unique_per_tenant(self, tenant):
        RoleFactory(tenant=tenant, code="unique_role")
        with pytest.raises(IntegrityError):
            RoleFactory(tenant=tenant, code="unique_role")

    def test_same_code_allowed_across_tenants(self, tenant):
        other = TenantFactory()
        RoleFactory(tenant=tenant, code="shared")
        RoleFactory(tenant=other, code="shared")
        assert Role.objects.filter(code="shared").count() == 2

    def test_role_permission_link_unique(self, tenant):
        role = RoleFactory(tenant=tenant)
        permission = PermissionFactory()
        RolePermission.objects.create(role=role, permission=permission, allow=True)
        with pytest.raises(IntegrityError):
            RolePermission.objects.create(role=role, permission=permission, allow=False)

    def test_role_soft_delete_hides_row(self, tenant):
        role = RoleFactory(tenant=tenant)
        role.delete()
        assert not Role.objects.filter(pk=role.pk).exists()
        assert Role.objects.all_with_deleted().filter(pk=role.pk).exists()

    def test_tenant_isolation(self, tenant):
        other = TenantFactory()
        RoleFactory(tenant=tenant, code="only_this_tenant")
        assert not Role.objects.filter(tenant=other, code="only_this_tenant").exists()


class TestRoleHierarchy:
    def test_edge_unique(self, tenant):
        child = RoleFactory(tenant=tenant)
        parent = RoleFactory(tenant=tenant)
        RoleHierarchy.objects.create(child_role=child, parent_role=parent)
        with pytest.raises(IntegrityError):
            RoleHierarchy.objects.create(child_role=child, parent_role=parent)


class TestRoleGroup:
    def test_group_code_unique_per_tenant(self, tenant):
        RoleGroupFactory(tenant=tenant, code="sales_ops")
        with pytest.raises(IntegrityError):
            RoleGroupFactory(tenant=tenant, code="sales_ops")

    def test_membership_unique(self, tenant):
        group = RoleGroupFactory(tenant=tenant)
        role = RoleFactory(tenant=tenant)
        RoleGroupMembership.objects.create(group=group, role=role)
        with pytest.raises(IntegrityError):
            RoleGroupMembership.objects.create(group=group, role=role)

    def test_group_soft_delete_hides_row(self, tenant):
        group = RoleGroupFactory(tenant=tenant)
        group.delete()
        assert not RoleGroup.objects.filter(pk=group.pk).exists()


class TestAssignments:
    def test_assignment_unique_tenant_user_role(self, tenant):
        user = UserFactory()
        role = RoleFactory(tenant=tenant)
        UserRoleAssignment.objects.create(tenant=tenant, user=user, role=role, is_active=True)
        with pytest.raises(IntegrityError):
            UserRoleAssignment.objects.create(tenant=tenant, user=user, role=role, is_active=True)

    def test_override_unique_tenant_user_permission(self, tenant):
        user = UserFactory()
        permission = PermissionFactory()
        UserPermissionOverride.objects.create(tenant=tenant, user=user, permission=permission, allow=True)
        with pytest.raises(IntegrityError):
            UserPermissionOverride.objects.create(tenant=tenant, user=user, permission=permission, allow=False)


class TestRoleVersion:
    def test_version_unique_per_role(self, tenant):
        role = RoleFactory(tenant=tenant)
        RoleVersion.objects.create(role=role, version=1, snapshot={"name": "v1"})
        with pytest.raises(IntegrityError):
            RoleVersion.objects.create(role=role, version=1, snapshot={"name": "v1-again"})


class TestTenantBootstrapSignal:
    def test_creating_tenant_provisions_roles(self, db):
        tenant = TenantFactory()
        assert Role.objects.filter(tenant=tenant, code="admin").exists()
        assert Role.objects.filter(tenant=tenant, code="member").exists()

    def test_bootstrap_respects_setting(self, db, settings):
        settings.RBAC_BOOTSTRAP_ON_TENANT_CREATE = False
        tenant = TenantFactory()
        assert not Role.objects.filter(tenant=tenant).exists()

    def test_bootstrap_only_runs_on_create(self, tenant):
        tenant.name = "Renamed"
        tenant.save()
        assert Role.objects.filter(tenant=tenant).count() == 2

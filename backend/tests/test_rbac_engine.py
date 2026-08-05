"""Engine-level tests: resolver inheritance, effective-permission precedence,
cache invalidation and superuser bypass."""

from __future__ import annotations

import pytest

from apps.rbac.constants import PERMISSION_CATALOG
from apps.rbac.engine import PermissionCache, PermissionEngine, PermissionResolver
from apps.rbac.models import Permission, Role, RolePermission, UserPermissionOverride
from apps.rbac.services import RoleAssignmentService
from tests.factories import RoleFactory

pytestmark = pytest.mark.django_db

CATALOG_ITEM_READ = "catalog.item.read"
CATALOG_ITEM_CREATE = "catalog.item.create"
INVENTORY_STOCK_READ = "inventory.stock.read"
INVENTORY_STOCK_CREATE = "inventory.stock.create"
POS_MANAGE = "pos.manage"


def _permission(code: str) -> Permission:
    return Permission.objects.get(code=code)


def _grant(role: Role, code: str, allow: bool = True) -> RolePermission:
    return RolePermission.objects.create(role=role, permission=_permission(code), allow=allow)


def _assign(user, role: Role) -> None:
    user.tenants.add(role.tenant)
    RoleAssignmentService().assign(user=user, role=role, actor=None, reason="test")


class TestResolver:
    def test_direct_links_are_reported_as_direct(self, tenant):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        result = PermissionResolver().role_permission_map(role)
        assert result[CATALOG_ITEM_READ] == (True, "direct")

    def test_direct_link_overrides_inherited(self, tenant):
        parent = RoleFactory(tenant=tenant)
        child = RoleFactory(tenant=tenant)
        _grant(parent, CATALOG_ITEM_READ, allow=True)
        _grant(child, CATALOG_ITEM_READ, allow=False)

        from apps.rbac.services import RoleHierarchyService

        RoleHierarchyService().add_parent(child, parent, actor=None)

        result = PermissionResolver().role_permission_map(child)
        assert result[CATALOG_ITEM_READ] == (False, "direct")

    def test_inherited_links_resolve_transitively(self, tenant):
        top = RoleFactory(tenant=tenant)
        middle = RoleFactory(tenant=tenant)
        child = RoleFactory(tenant=tenant)
        _grant(top, CATALOG_ITEM_CREATE, allow=True)

        from apps.rbac.services import RoleHierarchyService

        service = RoleHierarchyService()
        service.add_parent(middle, top, actor=None)
        service.add_parent(child, middle, actor=None)

        result = PermissionResolver().role_permission_map(child)
        assert result[CATALOG_ITEM_CREATE] == (True, "inherited")

    def test_mixed_sources_reported_correctly(self, tenant):
        parent = RoleFactory(tenant=tenant)
        child = RoleFactory(tenant=tenant)
        _grant(parent, CATALOG_ITEM_READ, allow=True)
        _grant(parent, INVENTORY_STOCK_READ, allow=True)
        _grant(child, INVENTORY_STOCK_READ, allow=False)
        _grant(child, POS_MANAGE, allow=True)

        from apps.rbac.services import RoleHierarchyService

        RoleHierarchyService().add_parent(child, parent, actor=None)

        result = PermissionResolver().role_permission_map(child)
        assert result[CATALOG_ITEM_READ] == (True, "inherited")
        assert result[INVENTORY_STOCK_READ] == (False, "direct")
        assert result[POS_MANAGE] == (True, "direct")


class TestEngineEffective:
    def test_anonymous_user_has_nothing(self, tenant):
        engine = PermissionEngine()
        assert engine.effective_permissions(None, tenant) == set()

    def test_user_without_assignments_has_nothing(self, tenant, user):
        assert PermissionEngine().effective_permissions(user, tenant) == set()

    def test_granted_permission_is_returned(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _assign(user, role)
        engine = PermissionEngine()
        effective = engine.effective_permissions(user, tenant)
        assert CATALOG_ITEM_READ in effective
        assert INVENTORY_STOCK_READ not in effective

    def test_has_permission_and_point_checks(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _grant(role, INVENTORY_STOCK_READ)
        _assign(user, role)
        engine = PermissionEngine()
        assert engine.has_permission(user, CATALOG_ITEM_READ, tenant)
        assert engine.has_any(user, [POS_MANAGE, CATALOG_ITEM_READ], tenant)
        assert not engine.has_any(user, [POS_MANAGE], tenant)
        assert engine.has_all(user, [CATALOG_ITEM_READ, INVENTORY_STOCK_READ], tenant)
        assert not engine.has_all(user, [CATALOG_ITEM_READ, POS_MANAGE], tenant)

    def test_effective_permissions_are_tenant_scoped(self, tenant, user):
        from tests.factories import TenantFactory

        other = TenantFactory()
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _assign(user, role)
        engine = PermissionEngine()
        assert CATALOG_ITEM_READ in engine.effective_permissions(user, tenant)
        assert engine.effective_permissions(user, other) == set()

    def test_modules_and_module_access(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _assign(user, role)
        engine = PermissionEngine()
        assert "catalog" in engine.modules_for(user, tenant)
        assert engine.has_module_access(user, "catalog", tenant)
        assert not engine.has_module_access(user, "inventory", tenant)


class TestEnginePrecedence:
    def test_override_deny_beats_role_grant(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ, allow=True)
        _assign(user, role)
        UserPermissionOverride.objects.create(
            tenant=tenant, user=user, permission=_permission(CATALOG_ITEM_READ), allow=False
        )
        engine = PermissionEngine()
        assert not engine.has_permission(user, CATALOG_ITEM_READ, tenant)

    def test_override_allow_beats_role_deny(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ, allow=False)
        _assign(user, role)
        UserPermissionOverride.objects.create(
            tenant=tenant, user=user, permission=_permission(CATALOG_ITEM_READ), allow=True
        )
        engine = PermissionEngine()
        assert engine.has_permission(user, CATALOG_ITEM_READ, tenant)

    def test_grant_beats_denial_across_roles(self, tenant, user):
        denying = RoleFactory(tenant=tenant)
        granting = RoleFactory(tenant=tenant)
        _grant(denying, INVENTORY_STOCK_CREATE, allow=False)
        _grant(granting, INVENTORY_STOCK_CREATE, allow=True)
        _assign(user, denying)
        _assign(user, granting)
        engine = PermissionEngine()
        assert engine.has_permission(user, INVENTORY_STOCK_CREATE, tenant)

    def test_denial_wins_when_all_roles_deny(self, tenant, user):
        first = RoleFactory(tenant=tenant)
        second = RoleFactory(tenant=tenant)
        _grant(first, INVENTORY_STOCK_CREATE, allow=False)
        _grant(second, INVENTORY_STOCK_CREATE, allow=False)
        _assign(user, first)
        _assign(user, second)
        engine = PermissionEngine()
        assert not engine.has_permission(user, INVENTORY_STOCK_CREATE, tenant)

    def test_override_applies_after_role_union(self, tenant, user):
        denying = RoleFactory(tenant=tenant)
        granting = RoleFactory(tenant=tenant)
        _grant(denying, INVENTORY_STOCK_CREATE, allow=False)
        _grant(granting, INVENTORY_STOCK_CREATE, allow=True)
        _assign(user, denying)
        _assign(user, granting)
        UserPermissionOverride.objects.create(
            tenant=tenant, user=user, permission=_permission(INVENTORY_STOCK_CREATE), allow=False
        )
        engine = PermissionEngine()
        assert not engine.has_permission(user, INVENTORY_STOCK_CREATE, tenant)


class TestCache:
    def test_invalidate_bumps_version(self):
        cache = PermissionCache()
        before = cache.current_version()
        cache.invalidate()
        assert cache.current_version() == before + 1

    def test_stale_entries_are_not_read_after_invalidate(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _assign(user, role)
        link = RolePermission.objects.get(role=role, permission=_permission(CATALOG_ITEM_READ))
        engine = PermissionEngine()

        assert CATALOG_ITEM_READ in engine.effective_permissions(user, tenant)

        # Signal-free update: cache still holds the old (stale) result.
        RolePermission.objects.filter(pk=link.pk).update(allow=False)
        assert CATALOG_ITEM_READ in engine.effective_permissions(user, tenant)

        # After invalidation the recompute reflects the change.
        PermissionCache().invalidate()
        assert CATALOG_ITEM_READ not in engine.effective_permissions(user, tenant)

    def test_signal_mutations_invalidate_automatically(self, tenant, user):
        role = RoleFactory(tenant=tenant)
        _grant(role, CATALOG_ITEM_READ)
        _assign(user, role)
        engine = PermissionEngine()
        assert engine.has_permission(user, CATALOG_ITEM_READ, tenant)
        _grant(role, POS_MANAGE)
        assert engine.has_permission(user, POS_MANAGE, tenant)


class TestSuperuserBypass:
    def test_superuser_has_every_active_code(self, superuser, tenant):
        engine = PermissionEngine()
        effective = engine.effective_permissions(superuser, tenant)
        assert effective == set(Permission.objects.filter(is_active=True).values_list("code", flat=True))

    def test_superuser_passes_every_check(self, superuser, tenant):
        engine = PermissionEngine()
        assert engine.has_permission(superuser, CATALOG_ITEM_READ, tenant)
        assert engine.has_permission(superuser, "rbac.role.protected_manage", tenant)
        assert engine.has_module_access(superuser, "platform", tenant)
        assert engine.modules_for(superuser, tenant) == {c["code"].split(".")[0] for c in PERMISSION_CATALOG}

    def test_non_superuser_missing_permission_denied(self, tenant, user):
        engine = PermissionEngine()
        assert not engine.has_permission(user, "rbac.role.create", tenant)

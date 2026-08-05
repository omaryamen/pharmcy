"""Service-layer tests: role lifecycle, hierarchy, groups, assignments, guards,
bootstrap and the permission catalog service."""

from __future__ import annotations

import pytest

from apps.common.exceptions import ConflictError, NotFoundError
from apps.rbac.constants import ADMIN_ROLE_CODE, RBAC_PERMISSIONS
from apps.rbac.exceptions import (
    CircularInheritanceError,
    CrossTenantError,
    InactiveRoleError,
    InvalidPermissionCodeError,
    MissingRbacPermissionError,
    PermissionInUseError,
    PrivilegeEscalationError,
    ProtectedAssignmentError,
    ProtectedPermissionError,
    ProtectedRoleError,
    RoleInUseError,
)
from apps.rbac.models import Permission, Role, RolePermission, RoleVersion
from apps.rbac.services import (
    PermissionService,
    RoleAssignmentService,
    RoleBootstrapService,
    RoleGroupService,
    RoleHierarchyService,
    RoleService,
)
from tests.factories import RoleFactory, TenantFactory, UserFactory
from tests.helpers import as_request

pytestmark = pytest.mark.django_db

CATALOG_ITEM_READ = "catalog.item.read"
CATALOG_ITEM_CREATE = "catalog.item.create"


def _grant(role: Role, code: str, allow: bool = True) -> RolePermission:
    return RolePermission.objects.create(role=role, permission=Permission.objects.get(code=code), allow=allow)


def _role_with(tenant, code: str, permission_codes: list[str]) -> Role:
    role = RoleFactory(tenant=tenant, code=code)
    for pc in permission_codes:
        _grant(role, pc)
    return role


def _assign(user, role: Role, actor=None) -> None:
    user.tenants.add(role.tenant)
    RoleAssignmentService().assign(user=user, role=role, actor=actor, reason="test")


class TestRoleService:
    def test_create_persists_role_version_and_audit(self, tenant):
        role = RoleService().create({"tenant": tenant, "name": "Pharmacist", "code": "pharmacist"})
        assert role.code == "pharmacist"
        assert role.tenant_id == tenant.pk
        assert role.versions.count() == 1
        assert role.versions.first().version == 1
        assert role.audit_logs.filter(action="created").exists()

    def test_create_injects_tenant_from_context(self, tenant):
        with as_request(tenant=tenant):
            role = RoleService().create({"name": "Cashier", "code": "cashier"})
        assert role.tenant_id == tenant.pk

    def test_create_rejects_reserved_code(self, tenant):
        with pytest.raises(ProtectedRoleError):
            RoleService().create({"tenant": tenant, "name": "Admin copy", "code": ADMIN_ROLE_CODE})

    def test_create_rejects_invalid_code_format(self, tenant):
        with pytest.raises(ConflictError):
            RoleService().create({"tenant": tenant, "name": "Bad", "code": "Bad Code!"})

    def test_create_rejects_duplicate_code(self, tenant):
        RoleFactory(tenant=tenant, code="dupe")
        with pytest.raises(ConflictError):
            RoleService().create({"tenant": tenant, "name": "Dupe", "code": "dupe"})

    def test_create_requires_name(self, tenant):
        with pytest.raises(ConflictError):
            RoleService().create({"tenant": tenant, "code": "noname"})

    def test_create_protected_requires_privilege(self, tenant, user):
        actor = UserFactory()
        actor.tenants.add(tenant)
        # Actor may create roles but not manage protected ones.
        _role_with(tenant, "role_manager", [RBAC_PERMISSIONS["ROLE_CREATE"]])
        _assign(actor, Role.objects.get(tenant=tenant, code="role_manager"))
        with as_request(user=actor, tenant=tenant), pytest.raises(ProtectedRoleError):
            RoleService().create({"tenant": tenant, "name": "Super", "code": "super", "is_protected": True})

    def test_update_renames_and_bumps_version(self, tenant):
        role = RoleService().create({"tenant": tenant, "name": "Role", "code": "role"})
        updated = RoleService().update(role.pk, {"name": "Renamed"})
        assert updated.name == "Renamed"
        assert role.versions.count() == 2

    def test_update_protected_role_code_is_rejected(self, tenant):
        admin = Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE)
        with pytest.raises(ProtectedRoleError):
            RoleService().update(admin.pk, {"code": "super_admin"})

    def test_update_protected_role_name_is_allowed(self, tenant):
        admin = Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE)
        updated = RoleService().update(admin.pk, {"name": "Tenant Admin"})
        assert updated.name == "Tenant Admin"

    def test_set_permissions_replaces_links(self, tenant):
        role = RoleService().create({"tenant": tenant, "name": "Role", "code": "role"})
        RoleService().set_permissions(role, {CATALOG_ITEM_READ: True, CATALOG_ITEM_CREATE: False})
        assert {link.permission.code: link.allow for link in role.permission_links.select_related("permission")} == {
            CATALOG_ITEM_READ: True,
            CATALOG_ITEM_CREATE: False,
        }
        RoleService().set_permissions(role, {CATALOG_ITEM_READ: True})
        assert list(role.permission_links.values_list("permission__code", flat=True)) == [CATALOG_ITEM_READ]

    def test_set_permissions_rejects_unknown_code(self, tenant):
        role = RoleService().create({"tenant": tenant, "name": "Role", "code": "role"})
        with pytest.raises(ConflictError):
            RoleService().set_permissions(role, {"no.such.code": True})

    def test_clone_copies_links_and_parents(self, tenant):
        parent = RoleFactory(tenant=tenant, code="parent")
        role = RoleService().create({"tenant": tenant, "name": "Role", "code": "role"})
        RoleService().set_permissions(role, {CATALOG_ITEM_READ: True})
        RoleHierarchyService().add_parent(role, parent, actor=None)

        cloned = RoleService().clone(role, name="Clone", code="role_clone")
        assert cloned.tenant_id == tenant.pk
        assert set(cloned.permission_links.values_list("permission__code", flat=True)) == {CATALOG_ITEM_READ}
        assert set(cloned.parent_links.values_list("parent_role__code", flat=True)) == {"parent"}

    def test_delete_blocks_role_with_active_assignments(self, tenant, user):
        role = _role_with(tenant, "occupied", [CATALOG_ITEM_READ])
        _assign(user, role)
        with pytest.raises(RoleInUseError):
            RoleService().delete(role.pk)

    def test_delete_removes_unassigned_role(self, tenant):
        role = _role_with(tenant, "unused", [CATALOG_ITEM_READ])
        RoleService().delete(role.pk)
        assert not Role.objects.filter(pk=role.pk).exists()

    def test_requires_permission_for_actor(self, tenant, user):
        with as_request(user=user, tenant=tenant), pytest.raises(MissingRbacPermissionError):
            RoleService().create({"tenant": tenant, "name": "Nope", "code": "nope"})


class TestRoleHierarchyService:
    def test_add_and_remove_parent(self, tenant):
        child = RoleFactory(tenant=tenant, code="child")
        parent = RoleFactory(tenant=tenant, code="parent")
        service = RoleHierarchyService()
        service.add_parent(child, parent, actor=None)
        assert service.ancestors(child) == [parent]
        assert service.is_ancestor(parent, child)
        assert service.remove_parent(child, parent, actor=None) is True

    def test_cycle_is_rejected(self, tenant):
        first = RoleFactory(tenant=tenant, code="first")
        second = RoleFactory(tenant=tenant, code="second")
        service = RoleHierarchyService()
        service.add_parent(second, first, actor=None)
        with pytest.raises(CircularInheritanceError):
            service.add_parent(first, second, actor=None)

    def test_self_parent_is_rejected(self, tenant):
        role = RoleFactory(tenant=tenant, code="solo")
        with pytest.raises(CircularInheritanceError):
            RoleHierarchyService().add_parent(role, role, actor=None)

    def test_cross_tenant_parent_is_rejected(self, tenant):
        other = TenantFactory()
        child = RoleFactory(tenant=tenant, code="child")
        parent = RoleFactory(tenant=other, code="parent")
        with pytest.raises(CrossTenantError):
            RoleHierarchyService().add_parent(child, parent, actor=None)


class TestRoleGroupService:
    def test_create_injects_tenant_from_context(self, tenant):
        with as_request(tenant=tenant):
            group = RoleGroupService().create({"name": "Ops", "code": "ops"})
        assert group.tenant_id == tenant.pk

    def test_create_rejects_duplicate_code(self, tenant):
        with as_request(tenant=tenant):
            RoleGroupService().create({"name": "Ops", "code": "ops"})
            with pytest.raises(ConflictError):
                RoleGroupService().create({"name": "Ops 2", "code": "ops"})

    def test_set_roles_replaces_membership(self, tenant):
        first = RoleFactory(tenant=tenant, code="first")
        second = RoleFactory(tenant=tenant, code="second")
        with as_request(tenant=tenant):
            group = RoleGroupService().create({"name": "Ops", "code": "ops"})
            RoleGroupService().set_roles(group, [first.pk, second.pk])
            assert set(group.roles.values_list("code", flat=True)) == {"first", "second"}
            RoleGroupService().set_roles(group, [first.pk])
            assert list(group.roles.values_list("code", flat=True)) == ["first"]

    def test_set_roles_rejects_cross_tenant_roles(self, tenant):
        other = TenantFactory()
        foreign = RoleFactory(tenant=other, code="foreign")
        with as_request(tenant=tenant):
            group = RoleGroupService().create({"name": "Ops", "code": "ops"})
            with pytest.raises(ConflictError):
                RoleGroupService().set_roles(group, [foreign.pk])


class TestRoleAssignmentService:
    def test_assign_creates_active_assignment(self, tenant, user):
        user.tenants.add(tenant)
        role = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        assignment = RoleAssignmentService().assign(user=user, role=role, actor=None, reason="hired")
        assert assignment.is_active is True
        assert assignment.is_primary is False
        assert assignment.reason == "hired"

    def test_assign_requires_tenant_membership(self, tenant, user):
        role = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        with pytest.raises(ConflictError):
            RoleAssignmentService().assign(user=user, role=role, actor=None)

    def test_assign_rejects_inactive_role(self, tenant, user):
        user.tenants.add(tenant)
        role = _role_with(tenant, "disabled", [CATALOG_ITEM_READ])
        Role.objects.filter(pk=role.pk).update(is_active=False)
        role.refresh_from_db()
        with pytest.raises(InactiveRoleError):
            RoleAssignmentService().assign(user=user, role=role, actor=None)

    def test_assign_promotes_single_primary(self, tenant, user):
        user.tenants.add(tenant)
        first = _role_with(tenant, "first", [CATALOG_ITEM_READ])
        second = _role_with(tenant, "second", [CATALOG_ITEM_READ])
        service = RoleAssignmentService()
        service.assign(user=user, role=first, actor=None, is_primary=True)
        service.assign(user=user, role=second, actor=None, is_primary=True)
        primaries = [a for a in service.list_for_user(user, tenant) if a.is_primary]
        assert len(primaries) == 1
        assert primaries[0].role.code == "second"

    def test_reassign_reactivates_soft_revoked(self, tenant, user):
        user.tenants.add(tenant)
        role = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        service = RoleAssignmentService()
        service.assign(user=user, role=role, actor=None)
        service.revoke(user=user, role=role, actor=None)
        assert service.active_roles_for_user(user, tenant) == []
        again = service.assign(user=user, role=role, actor=None)
        assert again.is_active is True
        assert service.active_roles_for_user(user, tenant) == [role]

    def test_revoke_missing_assignment_raises_not_found(self, tenant, user):
        user.tenants.add(tenant)
        role = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        with pytest.raises(NotFoundError):
            RoleAssignmentService().revoke(user=user, role=role, actor=None)

    def test_last_admin_cannot_be_revoked(self, tenant, user):
        user.tenants.add(tenant)
        admin = Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE)
        RoleAssignmentService().assign(user=user, role=admin, actor=None)
        with pytest.raises(ProtectedAssignmentError):
            RoleAssignmentService().revoke(user=user, role=admin, actor=None)

    def test_second_admin_can_be_revoked(self, tenant):
        first = UserFactory()
        second = UserFactory()
        first.tenants.add(tenant)
        second.tenants.add(tenant)
        admin = Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE)
        service = RoleAssignmentService()
        service.assign(user=first, role=admin, actor=None)
        service.assign(user=second, role=admin, actor=None)
        service.revoke(user=first, role=admin, actor=None)
        assert service.active_roles_for_user(first, tenant) == []

    def test_escalation_guard_blocks_broad_grant(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        actor.tenants.add(tenant)
        target.tenants.add(tenant)
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"]]))
        broad = _role_with(tenant, "broad", [RBAC_PERMISSIONS["ROLE_CREATE"], RBAC_PERMISSIONS["ROLE_DELETE"]])
        with as_request(user=actor, tenant=tenant), pytest.raises(PrivilegeEscalationError):
            RoleAssignmentService().assign(user=target, role=broad, actor=actor)

    def test_escalation_guard_allows_subset_grant(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        actor.tenants.add(tenant)
        target.tenants.add(tenant)
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"], CATALOG_ITEM_READ]))
        cashier = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        with as_request(user=actor, tenant=tenant):
            assignment = RoleAssignmentService().assign(user=target, role=cashier, actor=actor)
        assert assignment.is_active is True

    def test_missing_assignment_permission_blocked(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        actor.tenants.add(tenant)
        target.tenants.add(tenant)
        _assign(actor, _role_with(tenant, "reader", [CATALOG_ITEM_READ]))
        cashier = _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        with as_request(user=actor, tenant=tenant), pytest.raises(MissingRbacPermissionError):
            RoleAssignmentService().assign(user=target, role=cashier, actor=actor)

    def test_set_user_roles_reconciles(self, tenant, user):
        user.tenants.add(tenant)
        _role_with(tenant, "cashier", [CATALOG_ITEM_READ])
        _role_with(tenant, "manager", [CATALOG_ITEM_CREATE])
        service = RoleAssignmentService()
        service.set_user_roles(user=user, tenant=tenant, role_codes=["cashier"], actor=None)
        result = service.set_user_roles(user=user, tenant=tenant, role_codes=["manager"], actor=None)
        assert result["assigned"] == ["manager"]
        assert result["removed"] == ["cashier"]
        assert {r.code for r in service.active_roles_for_user(user, tenant)} == {"manager"}


class TestPermissionService:
    def test_create_custom_permission(self):
        permission = PermissionService().create(
            {"code": "custom.module.read", "name": "Custom Read", "module": "custom"}
        )
        assert permission.is_system is False

    def test_create_rejects_invalid_code(self):
        with pytest.raises(InvalidPermissionCodeError):
            PermissionService().create({"code": "not-a-code", "name": "Bad", "module": "custom"})

    def test_create_rejects_duplicate_code(self):
        code = "custom.dupe.read"
        PermissionService().create({"code": code, "name": "First", "module": "custom"})
        with pytest.raises(ConflictError):
            PermissionService().create({"code": code, "name": "Second", "module": "custom"})

    def test_delete_protected_permission_blocked(self):
        system = Permission.objects.get(code=CATALOG_ITEM_READ)
        with pytest.raises(ProtectedPermissionError):
            PermissionService().delete(system.pk)

    def test_delete_in_use_permission_blocked(self, tenant):
        permission = Permission.objects.get(code=CATALOG_ITEM_READ)
        role = _role_with(tenant, "owner", [CATALOG_ITEM_READ])
        assert permission.role_links.filter(role=role).exists()
        permission.is_system = False
        permission.save(update_fields=["is_system"])
        with pytest.raises(PermissionInUseError):
            PermissionService().delete(permission.pk)

    def test_sync_catalog_is_idempotent_and_reconciling(self):
        catalog = [
            {
                "code": "sync.a.read",
                "name": "A Read",
                "module": "sync",
                "category": "general",
                "action": "read",
                "scope": "tenant",
            },
            {
                "code": "sync.b.read",
                "name": "B Read",
                "module": "sync",
                "category": "general",
                "action": "read",
                "scope": "tenant",
            },
        ]
        first = PermissionService().sync_catalog(catalog=catalog)
        assert first["created"] == 2
        second = PermissionService().sync_catalog(catalog=catalog)
        assert second["created"] == 0
        assert second["updated"] == 2
        assert Permission.objects.filter(code__startswith="sync.").count() == 2

    def test_sync_catalog_deactivates_removed_codes(self):
        catalog = [
            {
                "code": "sync.only.read",
                "name": "Only",
                "module": "sync",
                "category": "general",
                "action": "read",
                "scope": "tenant",
            },
        ]
        PermissionService().sync_catalog(catalog=catalog)
        assert Permission.objects.get(code="sync.only.read").is_active is True
        PermissionService().sync_catalog(catalog=[])
        assert Permission.objects.get(code="sync.only.read").is_active is False


class TestRoleBootstrapService:
    def test_ensure_tenant_defaults_is_idempotent(self, tenant):
        result = RoleBootstrapService().ensure_tenant_defaults(tenant)
        assert result == {"admin": False, "member": False}

    def test_ensure_tenant_defaults_creates_when_missing(self):
        tenant = TenantFactory()
        # Hard-remove the admin role (as if never bootstrapped).
        Role.objects.all_with_deleted().get(tenant=tenant, code=ADMIN_ROLE_CODE).hard_delete()
        result = RoleBootstrapService().ensure_tenant_defaults(tenant)
        assert result["admin"] is True
        assert result["member"] is False
        assert Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE).is_protected is True

    def test_ensure_tenant_defaults_restores_soft_deleted_role(self):
        tenant = TenantFactory()
        admin = Role.objects.get(tenant=tenant, code=ADMIN_ROLE_CODE)
        admin.delete()
        assert not Role.objects.filter(pk=admin.pk).exists()
        result = RoleBootstrapService().ensure_tenant_defaults(tenant)
        assert result == {"admin": False, "member": False}
        restored = Role.objects.get(pk=admin.pk)
        assert restored.is_deleted is False
        assert restored.is_active is True


class TestRoleVersionHistory:
    def test_history_is_pruned_to_limit(self, tenant, settings):
        settings.RBAC_ROLE_HISTORY_MAX_VERSIONS = 3
        role = RoleService().create({"tenant": tenant, "name": "Role", "code": "role"})
        for i in range(5):
            RoleService().update(role.pk, {"name": f"Role {i}"})
        assert role.versions.count() <= 3
        assert RoleVersion.objects.filter(role=role).count() <= 3

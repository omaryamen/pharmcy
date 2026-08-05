"""Role inheritance management.

Roles in the same tenant may declare parents. Inheritance is checked for
cycles before any edge is created and changes invalidate the permission
cache (a parent's grants flow to every descendant immediately).
"""

from __future__ import annotations

from django.db import transaction

from apps.common.utils.context import get_current_user

from ..constants import RBAC_PERMISSIONS
from ..engine import PermissionCache, PermissionEngine
from ..exceptions import CircularInheritanceError, CrossTenantError, MissingRbacPermissionError, ProtectedRoleError
from ..models import Role, RoleHierarchy
from ..repositories import RoleHierarchyRepository


class RoleHierarchyService:
    def __init__(self, hierarchy_repository: RoleHierarchyRepository | None = None) -> None:
        self.hierarchy_repository = hierarchy_repository or RoleHierarchyRepository()

    @transaction.atomic
    def add_parent(self, child: Role, parent: Role, actor=None) -> RoleHierarchy:
        self._validate_pair(child, parent)
        self._assert_can_manage(child, actor)
        link = self.hierarchy_repository.link(child.pk, parent.pk)
        PermissionCache().invalidate()
        return link

    @transaction.atomic
    def remove_parent(self, child: Role, parent: Role, actor=None) -> bool:
        self._validate_pair(child, parent)
        self._assert_can_manage(child, actor)
        removed = self.hierarchy_repository.unlink(child.pk, parent.pk)
        PermissionCache().invalidate()
        return removed

    def ancestors(self, role: Role) -> list[Role]:
        ids = self.hierarchy_repository.ancestors(role.pk)
        return list(Role.objects.filter(pk__in=ids).order_by("name"))

    def descendants(self, role: Role) -> list[Role]:
        ids = self.hierarchy_repository.descendants(role.pk)
        return list(Role.objects.filter(pk__in=ids).order_by("name"))

    def is_ancestor(self, ancestor: Role, role: Role) -> bool:
        return ancestor.pk in self.hierarchy_repository.ancestors(role.pk)

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def _validate_pair(self, child: Role, parent: Role) -> None:
        if child.tenant_id != parent.tenant_id:
            raise CrossTenantError()
        if child.pk == parent.pk:
            raise CircularInheritanceError()
        if self.hierarchy_repository.has_cycle(child.pk, parent.pk):
            raise CircularInheritanceError()

    def _assert_can_manage(self, role: Role, actor) -> None:
        actor = actor or get_current_user()
        if actor is None or actor.is_superuser or not getattr(actor, "is_authenticated", False):
            return
        engine = PermissionEngine()
        if role.is_protected and not engine.has_permission(
            actor, RBAC_PERMISSIONS["ROLE_PROTECTED_MANAGE"], role.tenant
        ):
            raise ProtectedRoleError()
        if not engine.has_permission(actor, RBAC_PERMISSIONS["ROLE_UPDATE"], role.tenant):
            raise MissingRbacPermissionError()

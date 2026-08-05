"""Role group service — named bundles of roles for bulk assignment."""

from __future__ import annotations

from django.db import transaction

from apps.common.exceptions import ConflictError
from apps.common.services.base import BaseService
from apps.common.utils.context import get_current_tenant, get_current_user

from ..constants import RBAC_PERMISSIONS
from ..engine import PermissionCache, PermissionEngine
from ..exceptions import MissingRbacPermissionError
from ..models import Role, RoleGroup
from ..repositories import RoleGroupMembershipRepository, RoleGroupRepository


class RoleGroupService(BaseService[RoleGroup]):
    model = RoleGroup
    repository_class = RoleGroupRepository

    def __init__(self, repository: RoleGroupRepository | None = None) -> None:
        super().__init__(repository)
        self.membership_repository = RoleGroupMembershipRepository()

    @transaction.atomic
    def create(self, data: dict) -> RoleGroup:
        self._assert_can(RBAC_PERMISSIONS["GROUP_CREATE"])
        payload = dict(data)
        if payload.get("tenant") is None:
            current = get_current_tenant()
            if current is not None:
                payload["tenant"] = current
        payload["code"] = payload.get("code", "").strip().lower()
        if not payload.get("code") or not payload.get("name"):
            raise ConflictError("Both 'name' and 'code' are required for a role group.")
        if self.repository.exists(tenant=payload.get("tenant"), code=payload["code"]):
            raise ConflictError(f"A role group with code '{payload['code']}' already exists.")
        group = self.repository.create(**payload)
        PermissionCache().invalidate()
        return group

    @transaction.atomic
    def update(self, id, data: dict) -> RoleGroup:
        group = self.get(id)
        self._assert_can(RBAC_PERMISSIONS["GROUP_UPDATE"])
        payload = dict(data)
        if "code" in payload:
            payload["code"] = payload["code"].strip().lower()
            if payload["code"] != group.code and self.repository.exists(tenant=group.tenant, code=payload["code"]):
                raise ConflictError(f"A role group with code '{payload['code']}' already exists.")
        group = self.repository.update(group, **payload)
        PermissionCache().invalidate()
        return group

    @transaction.atomic
    def delete(self, id) -> RoleGroup:
        group = self.get(id)
        self._assert_can(RBAC_PERMISSIONS["GROUP_DELETE"])
        group = self.repository.delete(group)
        PermissionCache().invalidate()
        return group

    @transaction.atomic
    def set_roles(self, group: RoleGroup, role_ids: list) -> None:
        self._assert_can(RBAC_PERMISSIONS["GROUP_UPDATE"])
        roles = Role.objects.filter(pk__in=role_ids, tenant=group.tenant)
        found = set(roles.values_list("pk", flat=True))
        missing = set(role_ids) - found
        if missing:
            raise ConflictError("One or more roles do not belong to this tenant.")
        self.membership_repository.replace_roles(group, role_ids)
        PermissionCache().invalidate()

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def _assert_can(self, code: str) -> None:
        from apps.common.utils.context import get_current_tenant

        actor = get_current_user()
        if actor is None or actor.is_superuser or not getattr(actor, "is_authenticated", False):
            return
        if not PermissionEngine().has_permission(actor, code, get_current_tenant()):
            raise MissingRbacPermissionError(f"Permission '{code}' is required.")

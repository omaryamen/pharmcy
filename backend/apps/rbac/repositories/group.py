"""Role group persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository

from ..models import RoleGroup, RoleGroupMembership


class RoleGroupRepository(BaseRepository[RoleGroup]):
    model = RoleGroup

    def get_by_code(self, tenant, code: str) -> RoleGroup | None:
        return self.get_or_none(tenant=tenant, code=code)


class RoleGroupMembershipRepository(BaseRepository[RoleGroupMembership]):
    model = RoleGroupMembership

    def replace_roles(self, group, role_ids: list) -> None:
        existing = {membership.role_id for membership in self.filter(group=group)}
        desired = set(role_ids)
        # Hard-delete removed memberships: the ``RoleGroup.roles`` M2M resolves
        # through the base manager, so soft-deleted rows would stay visible.
        for membership in self.filter(group=group).exclude(role_id__in=desired):
            membership.hard_delete()
        for role_id in desired - existing:
            self.create(group=group, role_id=role_id)

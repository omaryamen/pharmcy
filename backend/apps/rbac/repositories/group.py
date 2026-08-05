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
        for role_id in existing - desired:
            self.filter(group=group, role_id=role_id).delete()
        for role_id in desired - existing:
            self.create(group=group, role_id=role_id)

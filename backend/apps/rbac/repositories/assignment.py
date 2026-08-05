"""User assignment / override persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository

from ..models import UserPermissionOverride, UserRoleAssignment


class UserRoleAssignmentRepository(BaseRepository[UserRoleAssignment]):
    model = UserRoleAssignment

    def active_for_user(self, user, tenant) -> list[UserRoleAssignment]:
        return list(
            self.filter(user=user, tenant=tenant, is_active=True).select_related("role").order_by("created_at")
        )

    def active_for_role(self, role) -> list[UserRoleAssignment]:
        return list(self.filter(role=role, is_active=True).select_related("user"))

    def get_active(self, *, tenant, user, role) -> UserRoleAssignment | None:
        return self.get_or_none(tenant=tenant, user=user, role=role, is_active=True)

    def get_any(self, *, tenant, user, role) -> UserRoleAssignment | None:
        return self.get_or_none(tenant=tenant, user=user, role=role)

    def count_active_admins(self, tenant, role_code: str) -> int:
        return self.filter(tenant=tenant, is_active=True, role__code=role_code, role__is_protected=True).count()

    def demote_primaries(self, user, tenant, *, except_assignment=None) -> None:
        qs = self.filter(user=user, tenant=tenant, is_primary=True)
        if except_assignment is not None:
            qs = qs.exclude(pk=except_assignment.pk)
        qs.update(is_primary=False)


class UserPermissionOverrideRepository(BaseRepository[UserPermissionOverride]):
    model = UserPermissionOverride

    def for_user(self, user, tenant) -> list[UserPermissionOverride]:
        return list(self.filter(user=user, tenant=tenant).select_related("permission"))

    def get(self, *, tenant, user, permission) -> UserPermissionOverride | None:
        return self.get_or_none(tenant=tenant, user=user, permission=permission)

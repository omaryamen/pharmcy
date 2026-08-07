"""EmployeeProfile repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.users.models import EmployeeProfile


class EmployeeProfileRepository(BaseRepository[EmployeeProfile]):
    model = EmployeeProfile

    def get_for_user(self, user) -> EmployeeProfile | None:
        return self.get_or_none(user=user)

    def get_with_relations(self, tenant, user_id) -> EmployeeProfile | None:
        return (
            self.get_queryset()
            .select_related("user", "company", "tenant", "primary_branch", "manager", "direct_supervisor")
            .prefetch_related("branches")
            .filter(tenant=tenant, user_id=user_id)
            .first()
        )

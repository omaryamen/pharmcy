"""Tenant repository for database persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.core.models import Tenant


class TenantRepository(BaseRepository[Tenant]):
    model = Tenant

    def get_by_code(self, code: str) -> Tenant | None:
        return self.get_or_none(code=code)

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.get_or_none(slug=slug)

    def get_with_details(self, pk) -> Tenant | None:
        return (
            self.get_queryset()
            .select_related("profile", "settings", "subscription", "owner")
            .prefetch_related("domains")
            .filter(pk=pk)
            .first()
        )

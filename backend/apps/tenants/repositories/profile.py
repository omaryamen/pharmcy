"""Tenant Profile repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.tenants.models import TenantProfile


class TenantProfileRepository(BaseRepository[TenantProfile]):
    model = TenantProfile

    def get_for_tenant(self, tenant) -> TenantProfile | None:
        return self.get_or_none(tenant=tenant)

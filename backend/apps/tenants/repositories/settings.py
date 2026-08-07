"""Tenant Settings repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.tenants.models import TenantSettings


class TenantSettingsRepository(BaseRepository[TenantSettings]):
    model = TenantSettings

    def get_for_tenant(self, tenant) -> TenantSettings | None:
        return self.get_or_none(tenant=tenant)

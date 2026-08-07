"""Tenant Domain repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.tenants.models import TenantDomain


class TenantDomainRepository(BaseRepository[TenantDomain]):
    model = TenantDomain

    def get_by_name(self, domain_name: str) -> TenantDomain | None:
        return self.get_or_none(domain_name=domain_name.lower().strip())

    def get_for_tenant(self, tenant) -> list[TenantDomain]:
        return list(self.filter(tenant=tenant))

"""Supplier repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.suppliers.models import Supplier


class SupplierRepository(BaseRepository[Supplier]):
    model = Supplier

    def get_by_code(self, tenant, code: str) -> Supplier | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

    def get_by_legal_name(self, tenant, legal_name: str) -> Supplier | None:
        return self.get_or_none(tenant=tenant, legal_name=legal_name.strip())

    def for_tenant(self, tenant) -> list[Supplier]:
        return list(self.filter(tenant=tenant))

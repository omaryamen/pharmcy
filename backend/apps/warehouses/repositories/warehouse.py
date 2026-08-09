"""Warehouse repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.warehouses.models import Warehouse


class WarehouseRepository(BaseRepository[Warehouse]):
    model = Warehouse

    def get_by_code(self, tenant, code: str) -> Warehouse | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

    def get_by_name(self, tenant, company_id, name: str) -> Warehouse | None:
        return self.get_or_none(tenant=tenant, company_id=company_id, name=name.strip())

    def for_company(self, tenant, company_id) -> list[Warehouse]:
        return list(self.filter(tenant=tenant, company_id=company_id))

    def for_branch(self, tenant, branch_id) -> list[Warehouse]:
        return list(self.filter(tenant=tenant, branch_id=branch_id))

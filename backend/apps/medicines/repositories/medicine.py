"""Medicine repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.medicines.models import Medicine


class MedicineRepository(BaseRepository[Medicine]):
    model = Medicine

    def get_by_code(self, tenant, code: str) -> Medicine | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

    def get_by_sku(self, tenant, sku: str) -> Medicine | None:
        return self.get_or_none(tenant=tenant, sku=sku.strip())

    def get_by_barcode(self, tenant, barcode: str) -> Medicine | None:
        return self.get_or_none(tenant=tenant, barcode=barcode.strip())

    def for_tenant(self, tenant) -> list[Medicine]:
        return list(self.filter(tenant=tenant))

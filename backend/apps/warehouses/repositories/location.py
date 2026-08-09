"""Storage Location repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.warehouses.models import StorageLocation


class StorageLocationRepository(BaseRepository[StorageLocation]):
    model = StorageLocation

    def get_by_code(self, warehouse_id, code: str) -> StorageLocation | None:
        return self.get_or_none(warehouse_id=warehouse_id, code=code.strip())

    def for_warehouse(self, warehouse_id) -> list[StorageLocation]:
        return list(self.filter(warehouse_id=warehouse_id).select_related("parent", "warehouse"))

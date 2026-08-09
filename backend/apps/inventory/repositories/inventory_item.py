"""InventoryItem repository for stock location balance data operations."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.inventory.models import InventoryItem


class InventoryItemRepository(BaseRepository[InventoryItem]):
    model = InventoryItem

    def get_exact_stock_position(self, tenant, warehouse_id, storage_location_id, medicine_id, batch_id) -> InventoryItem | None:
        return self.get_or_none(
            tenant=tenant,
            warehouse_id=warehouse_id,
            storage_location_id=storage_location_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
        )

    def get_with_lock(self, tenant, item_id: str) -> InventoryItem | None:
        """Lock inventory item row for update to prevent concurrent race conditions."""
        return self.filter(tenant=tenant, pk=item_id).select_for_update().first()

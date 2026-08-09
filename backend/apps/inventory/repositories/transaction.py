"""InventoryTransaction repository for auditable stock movement queries."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.inventory.models import InventoryTransaction


class InventoryTransactionRepository(BaseRepository[InventoryTransaction]):
    model = InventoryTransaction

    def for_item(self, tenant, inventory_item_id: str) -> list[InventoryTransaction]:
        return list(self.filter(tenant=tenant, inventory_item_id=inventory_item_id).order_by("-created_at"))

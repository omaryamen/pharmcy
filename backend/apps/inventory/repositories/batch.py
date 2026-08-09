"""Batch repository for database access operations."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.inventory.models import Batch


class BatchRepository(BaseRepository[Batch]):
    model = Batch

    def get_by_batch_number(self, tenant, medicine_id, batch_number: str) -> Batch | None:
        return self.get_or_none(tenant=tenant, medicine_id=medicine_id, batch_number=batch_number.strip())

    def for_medicine(self, tenant, medicine_id) -> list[Batch]:
        return list(self.filter(tenant=tenant, medicine_id=medicine_id).order_by("expiry_date"))

"""Repository for StockMovement entity."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.common.repositories import BaseRepository
from apps.stock_movement.models import StockMovement


class StockMovementRepository(BaseRepository[StockMovement]):
    """Data access repository for StockMovement."""

    def __init__(self):
        super().__init__(StockMovement)

    def filter_by_tenant(self, tenant: Any) -> QuerySet[StockMovement]:
        return self.get_queryset().filter(tenant=tenant)

    def find_by_number(self, tenant: Any, movement_number: str) -> StockMovement | None:
        return self.filter_by_tenant(tenant).filter(movement_number=movement_number).first()

    def find_by_idempotency_key(self, tenant: Any, idempotency_key: str) -> StockMovement | None:
        if not idempotency_key:
            return None
        return self.filter_by_tenant(tenant).filter(idempotency_key=idempotency_key).first()

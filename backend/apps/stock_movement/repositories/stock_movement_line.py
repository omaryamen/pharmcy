"""Repository for StockMovementLine entity."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.common.repositories import BaseRepository
from apps.stock_movement.models import StockMovementLine


class StockMovementLineRepository(BaseRepository[StockMovementLine]):
    """Data access repository for StockMovementLine."""

    def __init__(self):
        super().__init__(StockMovementLine)

    def filter_by_movement(self, movement: Any) -> QuerySet[StockMovementLine]:
        return self.get_queryset().filter(movement=movement)

"""StockCount and StockCountLine repositories for data access operations."""

from __future__ import annotations

from typing import Any

from apps.common.repositories.base import BaseRepository
from apps.stock_adjustment.models import StockCount, StockCountLine, StockCountRecount, StockCountSession


class StockCountRepository(BaseRepository[StockCount]):
    model = StockCount

    def get_by_count_number(self, tenant: Any, count_number: str) -> StockCount | None:
        return self.get_or_none(tenant=tenant, count_number=count_number)

    def find_by_idempotency_key(self, tenant: Any, idempotency_key: str) -> StockCount | None:
        if not idempotency_key:
            return None
        return self.get_or_none(tenant=tenant, idempotency_key=idempotency_key)


class StockCountLineRepository(BaseRepository[StockCountLine]):
    model = StockCountLine


class StockCountSessionRepository(BaseRepository[StockCountSession]):
    model = StockCountSession


class StockCountRecountRepository(BaseRepository[StockCountRecount]):
    model = StockCountRecount

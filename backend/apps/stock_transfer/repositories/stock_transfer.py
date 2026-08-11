"""Repositories for StockTransfer data access operations."""

from __future__ import annotations

from typing import Any

from apps.common.repositories.base import BaseRepository
from apps.stock_transfer.models import (
    StockTransfer,
    StockTransferDiscrepancy,
    StockTransferHistory,
    StockTransferLine,
)


class StockTransferRepository(BaseRepository[StockTransfer]):
    model = StockTransfer

    def get_by_transfer_number(self, tenant: Any, transfer_number: str) -> StockTransfer | None:
        return self.get_or_none(tenant=tenant, transfer_number=transfer_number)

    def find_by_idempotency_key(self, tenant: Any, idempotency_key: str) -> StockTransfer | None:
        if not idempotency_key:
            return None
        return self.get_or_none(tenant=tenant, idempotency_key=idempotency_key)


class StockTransferLineRepository(BaseRepository[StockTransferLine]):
    model = StockTransferLine


class StockTransferDiscrepancyRepository(BaseRepository[StockTransferDiscrepancy]):
    model = StockTransferDiscrepancy

    def get_by_discrepancy_number(self, tenant: Any, discrepancy_number: str) -> StockTransferDiscrepancy | None:
        return self.get_or_none(tenant=tenant, discrepancy_number=discrepancy_number)


class StockTransferHistoryRepository(BaseRepository[StockTransferHistory]):
    model = StockTransferHistory

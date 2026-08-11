"""Repository layer for GoodsReceipt persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.goods_receipt.models import GoodsReceipt, GoodsReceiptLine


class GoodsReceiptRepository:
    """Repository encapsulating persistence operations for GoodsReceipt."""

    def get_queryset(self, tenant: Any) -> QuerySet[GoodsReceipt]:
        return GoodsReceipt.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, receipt_id: str) -> GoodsReceipt | None:
        return self.get_queryset(tenant).filter(pk=receipt_id).first()

    def find_by_number(self, tenant: Any, number: str) -> GoodsReceipt | None:
        return self.get_queryset(tenant).filter(receipt_number=number).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> GoodsReceipt | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> GoodsReceipt:
        return GoodsReceipt.objects.create(tenant=tenant, **kwargs)

    def update(self, receipt: GoodsReceipt, **kwargs: Any) -> GoodsReceipt:
        for field, value in kwargs.items():
            setattr(receipt, field, value)
        receipt.save()
        return receipt


class GoodsReceiptLineRepository:
    """Repository encapsulating persistence operations for GoodsReceiptLine."""

    def create(self, tenant: Any, **kwargs: Any) -> GoodsReceiptLine:
        return GoodsReceiptLine.objects.create(tenant=tenant, **kwargs)

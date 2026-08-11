"""Export repositories for apps.goods_receipt."""

from apps.goods_receipt.repositories.receipt_repository import GoodsReceiptLineRepository, GoodsReceiptRepository

__all__ = [
    "GoodsReceiptRepository",
    "GoodsReceiptLineRepository",
]

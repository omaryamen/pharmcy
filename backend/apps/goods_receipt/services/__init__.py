"""Export domain services for apps.goods_receipt."""

from apps.goods_receipt.services.goods_receipt_service import GoodsReceiptService
from apps.goods_receipt.services.number_generator import GoodsReceiptNumberGenerator

__all__ = [
    "GoodsReceiptNumberGenerator",
    "GoodsReceiptService",
]

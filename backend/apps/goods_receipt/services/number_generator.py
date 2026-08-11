"""Collision-safe sequence number generator for GoodsReceipt documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.goods_receipt.models import GoodsReceipt


class GoodsReceiptNumberGenerator:
    """Generates sequential GRN numbers (GRN-YYYY-XXXXXX)."""

    @transaction.atomic
    def generate_receipt_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"GRN-{year}-"

        last_receipt = (
            GoodsReceipt.objects.filter(tenant=tenant, receipt_number__startswith=prefix)
            .order_by("-receipt_number")
            .select_for_update()
            .first()
        )

        if not last_receipt:
            seq = 1
        else:
            try:
                seq = int(last_receipt.receipt_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

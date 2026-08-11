"""Sequence code generator for Stock Transfer documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.stock_transfer.models import StockTransfer, StockTransferDiscrepancy


class TransferNumberGenerator:
    """Generates unique document numbers for Stock Transfers and Discrepancies per tenant."""

    @transaction.atomic
    def generate_transfer_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"TRF-{year}-"

        last_doc = (
            StockTransfer.objects.filter(tenant=tenant, transfer_number__startswith=prefix)
            .select_for_update()
            .order_by("-transfer_number")
            .first()
        )

        seq = 1
        if last_doc and last_doc.transfer_number:
            try:
                part = last_doc.transfer_number.split("-")[-1]
                seq = int(part) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_discrepancy_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"DISC-{year}-"

        last_doc = (
            StockTransferDiscrepancy.objects.filter(tenant=tenant, discrepancy_number__startswith=prefix)
            .select_for_update()
            .order_by("-discrepancy_number")
            .first()
        )

        seq = 1
        if last_doc and last_doc.discrepancy_number:
            try:
                part = last_doc.discrepancy_number.split("-")[-1]
                seq = int(part) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

"""Configurable sequence number generator for Stock Movements."""

import datetime
from typing import Any

from django.db import transaction

from apps.stock_movement.models import MovementType, StockMovement


PREFIX_MAP = {
    MovementType.OPENING_BALANCE: "OPN",
    MovementType.RECEIPT: "REC",
    MovementType.ISSUE: "ISS",
    MovementType.SALE: "SAL",
    MovementType.SALE_RETURN: "SRT",
    MovementType.PURCHASE_RETURN: "PRT",
    MovementType.TRANSFER_OUT: "TRF",
    MovementType.TRANSFER_IN: "TRF",
    MovementType.ADJUSTMENT_IN: "ADJ",
    MovementType.ADJUSTMENT_OUT: "ADJ",
    MovementType.DAMAGE: "DMG",
    MovementType.EXPIRY: "EXP",
    MovementType.QUARANTINE: "QRN",
    MovementType.QUARANTINE_RELEASE: "QRL",
    MovementType.RESERVATION: "RSV",
    MovementType.RESERVATION_RELEASE: "RRL",
    MovementType.CORRECTION: "COR",
    MovementType.RECALL: "RCL",
    MovementType.OTHER: "STK",
}


class MovementNumberGenerator:
    """Generates unique, collision-safe stock movement document numbers e.g. TRF-2026-000001."""

    @transaction.atomic
    def generate_number(self, tenant: Any, movement_type: str) -> str:
        prefix = PREFIX_MAP.get(movement_type, "STK")
        year = datetime.date.today().year
        base_pattern = f"{prefix}-{year}-"

        latest_num = (
            StockMovement.objects.filter(
                tenant=tenant,
                movement_number__startswith=base_pattern,
            )
            .select_for_update()
            .order_by("-movement_number")
            .values_list("movement_number", flat=True)
            .first()
        )

        if not latest_num:
            seq = 1
        else:
            try:
                seq_str = latest_num.rsplit("-", 1)[-1]
                seq = int(seq_str) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{base_pattern}{seq:06d}"

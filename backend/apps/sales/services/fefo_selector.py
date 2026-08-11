"""FEFO (First Expiry, First Out) batch selector service for POS retail sales."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.utils import timezone

from apps.inventory.models import InventoryItem
from apps.inventory.models.enums import BatchStatus
from apps.sales.exceptions import InsufficientStockForSaleError
from apps.sales.validators import validate_batch_eligibility_for_sale

logger = logging.getLogger(__name__)


class FEFOBatchSelector:
    """Selects the earliest expiring valid batch for pharmaceutical retail sales."""

    def select_fefo_batch_for_sale(
        self,
        tenant: Any,
        warehouse: Any,
        storage_location: Any,
        medicine: Any,
        required_quantity: Decimal | float | int,
    ) -> tuple[Any, Decimal]:
        """Find the earliest expiring eligible batch with sufficient available stock balance."""
        req_qty = Decimal(str(required_quantity))
        today = timezone.now().date()

        items = (
            InventoryItem.objects.filter(
                tenant=tenant,
                warehouse=warehouse,
                storage_location=storage_location,
                medicine=medicine,
                on_hand_quantity__gt=Decimal("0.0000"),
                batch__status=BatchStatus.ACTIVE,
                batch__expiry_date__gt=today,
            )
            .select_related("batch")
            .order_by("batch__expiry_date", "created_at")
        )

        for item in items:
            batch = item.batch
            try:
                validate_batch_eligibility_for_sale(batch)
            except Exception:
                continue

            if item.available_quantity >= req_qty:
                logger.info("FEFO auto-selected batch %s (Expiry: %s) for medicine %s", batch.batch_number, batch.expiry_date, medicine.english_name)
                return batch, item.available_quantity

        raise InsufficientStockForSaleError(
            f"No eligible non-expired, non-recalled batch with {req_qty} available stock found for {medicine.english_name}."
        )

"""Validators for Enterprise Stock Movement Engine."""

from decimal import Decimal

from django.utils import timezone

from apps.inventory.models.enums import BatchStatus
from apps.stock_movement.exceptions import (
    BlockedBatchMovementForbiddenError,
    ExpiredBatchIssuedForbiddenError,
    LocationWarehouseMismatchError,
    RecalledBatchMovementForbiddenError,
    StockMovementValidationError,
)


def validate_positive_quantity(quantity: Decimal | float | int) -> Decimal:
    """Validate movement quantity is strictly positive (> 0.00)."""
    val = Decimal(str(quantity))
    if val <= Decimal("0.00"):
        raise StockMovementValidationError("Stock movement quantity must be strictly greater than zero.")
    return val


def validate_location_belongs_to_warehouse(location, warehouse) -> None:
    """Validate that storage location belongs to the given warehouse."""
    if location and warehouse:
        if str(location.warehouse_id) != str(warehouse.id):
            raise LocationWarehouseMismatchError(
                f"Storage location '{location.code}' does not belong to warehouse '{warehouse.code}'."
            )


def validate_batch_eligibility_for_outgoing_movement(batch, allow_expired: bool = False) -> None:
    """Validate that batch is active, non-expired, non-recalled, and non-blocked for outgoing issuance."""
    if not batch:
        return

    if batch.status == BatchStatus.RECALLED:
        raise RecalledBatchMovementForbiddenError(
            f"Batch '{batch.batch_number}' has been RECALLED and cannot be moved or issued."
        )

    if batch.status == BatchStatus.BLOCKED:
        raise BlockedBatchMovementForbiddenError(
            f"Batch '{batch.batch_number}' is BLOCKED and cannot be moved or issued."
        )

    if not allow_expired and (batch.is_expired or batch.status == BatchStatus.EXPIRED):
        raise ExpiredBatchIssuedForbiddenError(
            f"Batch '{batch.batch_number}' is EXPIRED (Expiry Date: {batch.expiry_date}) and cannot be issued."
        )

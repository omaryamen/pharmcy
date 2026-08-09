"""Validators for Enterprise Inventory & Batch Management."""

from __future__ import annotations

from decimal import Decimal

from apps.inventory.exceptions import (
    InvalidBatchDateError,
    InventoryBatchMismatchError,
    InventoryLocationMismatchError,
    NegativeStockForbiddenError,
)


def validate_batch_dates(manufacturing_date, expiry_date) -> None:
    if manufacturing_date and expiry_date and expiry_date < manufacturing_date:
        raise InvalidBatchDateError("Expiry date cannot be earlier than manufacturing date.")


def validate_inventory_location(storage_location, warehouse) -> None:
    if storage_location and warehouse and storage_location.warehouse_id != warehouse.id:
        raise InventoryLocationMismatchError("Storage location must belong to the specified warehouse.")


def validate_inventory_batch(batch, medicine) -> None:
    if batch and medicine and batch.medicine_id != medicine.id:
        raise InventoryBatchMismatchError("Batch must belong to the specified medicine master record.")


def validate_quantity_non_negative(quantity: Decimal | float | int, field_name: str = "Quantity") -> None:
    if Decimal(str(quantity)) < Decimal("0"):
        raise NegativeStockForbiddenError(f"{field_name} cannot be negative.")

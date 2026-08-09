"""Exceptions specific to Enterprise Inventory & Batch Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError, ValidationFailedError


class BatchNotFoundError(NotFoundError):
    code = "batch_not_found"
    message = "The requested batch record does not exist."


class DuplicateBatchNumberError(ConflictError):
    code = "duplicate_batch_number"
    message = "A batch with this batch number already exists for this medicine in this tenant."


class InvalidBatchDateError(ValidationFailedError):
    code = "invalid_batch_date"
    message = "Expiry date cannot be earlier than manufacturing date."


class BatchStatusError(BusinessRuleViolation):
    code = "batch_status_invalid"
    message = "The batch is not active or is blocked/recalled/expired for operational usage."


class InventoryItemNotFoundError(NotFoundError):
    code = "inventory_item_not_found"
    message = "The requested inventory item record does not exist."


class InsufficientStockError(BusinessRuleViolation):
    code = "insufficient_stock"
    message = "Insufficient available stock to perform the requested reservation or deduction."


class NegativeStockForbiddenError(BusinessRuleViolation):
    code = "negative_stock_forbidden"
    message = "Inventory stock quantities cannot be negative."


class InventoryLocationMismatchError(ValidationFailedError):
    code = "inventory_location_mismatch"
    message = "Storage location must belong to the specified warehouse and tenant scope."


class InventoryBatchMismatchError(ValidationFailedError):
    code = "inventory_batch_mismatch"
    message = "Batch must belong to the specified medicine and tenant scope."


class InventoryTransactionError(BusinessRuleViolation):
    code = "inventory_transaction_failed"
    message = "Failed to record stock transaction."

"""Domain exceptions for Enterprise Stock Movement Engine."""

from rest_framework import status
from rest_framework.exceptions import APIException


class StockMovementError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A stock movement domain error occurred."
    default_code = "stock_movement_error"


class StockMovementNotFoundError(StockMovementError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Requested stock movement was not found."
    default_code = "stock_movement_not_found"


class InvalidMovementStateError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock movement is in an invalid state for this operation."
    default_code = "invalid_movement_state"


class DuplicateIdempotencyKeyError(StockMovementError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A stock movement with this idempotency key has already been submitted."
    default_code = "duplicate_idempotency_key"


class MovementAlreadyProcessedError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock movement has already been processed."
    default_code = "movement_already_processed"


class MovementAlreadyCancelledError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock movement has already been cancelled."
    default_code = "movement_already_cancelled"


class MovementAlreadyReversedError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock movement has already been reversed."
    default_code = "movement_already_reversed"


class CannotReverseUnprocessedMovementError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Only completed stock movements can be reversed."
    default_code = "cannot_reverse_unprocessed_movement"


class InvalidMovementTypeError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Specified stock movement type is invalid or unsupported."
    default_code = "invalid_movement_type"


class StockMovementValidationError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock movement validation failed."
    default_code = "stock_movement_validation_error"


class LocationWarehouseMismatchError(StockMovementValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Storage location does not belong to the specified warehouse."
    default_code = "location_warehouse_mismatch"


class InsufficientAvailableStockError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Sufficient stock is not available for this outgoing movement."
    default_code = "insufficient_available_stock"


class ExpiredBatchIssuedForbiddenError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot issue or sell stock from an expired batch."
    default_code = "expired_batch_issued_forbidden"


class RecalledBatchMovementForbiddenError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot move stock from a recalled batch."
    default_code = "recalled_batch_movement_forbidden"


class BlockedBatchMovementForbiddenError(StockMovementError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot move stock from a blocked batch."
    default_code = "blocked_batch_movement_forbidden"

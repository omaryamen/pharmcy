"""Domain exception hierarchy for Enterprise Stock Transfer module."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class StockTransferError(APIException):
    """Base domain exception for Stock Transfer errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "stock_transfer_error"
    default_detail = "Stock transfer domain error occurred."


class InvalidTransferStateError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_transfer_state"
    default_detail = "The transfer is in an invalid state for this operation."


class TransferAlreadyDispatchedError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "transfer_already_dispatched"
    default_detail = "The transfer has already been dispatched and cannot be modified."


class TransferAlreadyReceivedError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "transfer_already_received"
    default_detail = "The transfer has already been received."


class TransferAlreadyCancelledError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "transfer_already_cancelled"
    default_detail = "The transfer has already been cancelled."


class TransferAlreadyReversedError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "transfer_already_reversed"
    default_detail = "The transfer has already been reversed."


class CannotCancelDispatchedTransferError(StockTransferError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cannot_cancel_dispatched_transfer"
    default_detail = "Cannot cancel a dispatched transfer. Use reversal workflow instead."


class InsufficientTransferStockError(StockTransferError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "insufficient_transfer_stock"
    default_detail = "Insufficient available stock at source location for picking/dispatch."


class InvalidBatchForTransferError(StockTransferError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_batch_for_transfer"
    default_detail = "Selected batch is expired, recalled, blocked, or quarantined and cannot be transferred."


class WrongMedicineReceivedError(StockTransferError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "wrong_medicine_received"
    default_detail = "Received medicine does not match the requested transfer line medicine."


class SelfApprovalForbiddenError(StockTransferError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "self_approval_forbidden"
    default_detail = "Requester user cannot approve their own stock transfer."


class DuplicateTransferOperationError(StockTransferError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "duplicate_transfer_operation"
    default_detail = "This transfer operation has already been performed (idempotency key match)."

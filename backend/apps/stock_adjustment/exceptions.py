"""Domain exceptions for Enterprise Stock Adjustment & Stock Count module."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class StockAdjustmentError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A stock adjustment error occurred."
    default_code = "stock_adjustment_error"


class InvalidCountStateError(StockAdjustmentError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Stock count is in an invalid state for this operation."
    default_code = "invalid_count_state"


class CountAlreadySubmittedError(StockAdjustmentError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock count has already been submitted."
    default_code = "count_already_submitted"


class CountAlreadyReconciledError(StockAdjustmentError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Stock count has already been reconciled."
    default_code = "count_already_reconciled"


class CountAlreadyCancelledError(StockAdjustmentError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock count has already been cancelled."
    default_code = "count_already_cancelled"


class UnauthorizedBlindCountAccessError(StockAdjustmentError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Access to system quantity is restricted during blind counting."
    default_code = "unauthorized_blind_count_access"


class InventoryLockedError(StockAdjustmentError):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Inventory for the specified scope is locked due to an active count session."
    default_code = "inventory_locked"


class VarianceExceedsThresholdError(StockAdjustmentError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Stock count variance exceeds the authorized threshold and requires higher approval."
    default_code = "variance_exceeds_threshold"


class SelfApprovalForbiddenError(StockAdjustmentError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Separation of duties policy forbids counters from approving their own variance."
    default_code = "self_approval_forbidden"


class DuplicateReconciliationError(StockAdjustmentError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Stock count reconciliation has already been executed."
    default_code = "duplicate_reconciliation"

"""Domain exception hierarchy for Enterprise Customer Accounts Receivable (AR)."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class AROperationError(APIException):
    """Base domain exception for Accounts Receivable operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "ar_operation_error"
    default_detail = "An Accounts Receivable domain error occurred."


class InvalidARStateError(AROperationError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_ar_state"
    default_detail = "Receivable or payment is in an invalid status for this operation."


class ExceedsOutstandingBalanceError(AROperationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_outstanding_balance"
    default_detail = "Payment or credit allocation amount exceeds net outstanding receivable balance."


class OverpaymentRejectedError(AROperationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "overpayment_rejected"
    default_detail = "Payment amount exceeds total outstanding obligations and overpayment policy rejects unallocated excess."


class CreditLimitExceededError(AROperationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "credit_limit_exceeded"
    default_detail = "Requested credit sale exceeds customer credit limit."


class SelfApprovalForbiddenError(AROperationError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "self_approval_forbidden"
    default_detail = "Separation of duties violation: creator cannot approve own adjustment or write-off."


class PaymentAlreadyReversedError(AROperationError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "payment_already_reversed"
    default_detail = "Customer payment has already been reversed."

"""Domain exception hierarchy for Enterprise Goods Receipt & Receiving Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class GoodsReceiptDomainError(APIException):
    """Base domain exception for goods receipt operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "goods_receipt_domain_error"
    default_detail = "A goods receipt error occurred."


class InvalidReceiptStateError(GoodsReceiptDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_receipt_state"
    default_detail = "The goods receipt is in an invalid state for this operation."


class ExpiryValidationError(GoodsReceiptDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expiry_validation_error"
    default_detail = "Batch expiry date is invalid or has expired."


class RecalledBatchReceivingError(GoodsReceiptDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "recalled_batch_receiving_error"
    default_detail = "Cannot receive a batch that is marked as recalled or blocked."


class OverReceivingPolicyError(GoodsReceiptDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "over_receiving_policy_error"
    default_detail = "Received quantity exceeds Purchase Order line quantity beyond allowed tolerance."


class AlreadyPostedError(GoodsReceiptDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "already_posted"
    default_detail = "Goods receipt has already been posted to inventory."


class CannotReverseUnpostedReceiptError(GoodsReceiptDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cannot_reverse_unposted"
    default_detail = "Cannot reverse a goods receipt that has not been posted."

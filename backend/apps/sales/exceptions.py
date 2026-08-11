"""Domain exception hierarchy for Enterprise POS & Sales Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class SalesDomainError(APIException):
    """Base domain exception for sales operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "sales_domain_error"
    default_detail = "A sales domain error occurred."


class InsufficientStockForSaleError(SalesDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "insufficient_stock_for_sale"
    default_detail = "Insufficient available stock to complete this sale."


class IneligibleBatchForSaleError(SalesDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "ineligible_batch_for_sale"
    default_detail = "Selected medicine batch is expired, recalled, or quarantined and cannot be sold."


class InvalidSaleStateError(SalesDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_sale_state"
    default_detail = "The sales invoice is in an invalid state for this operation."


class ExceedsCustomerCreditLimitError(SalesDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_credit_limit"
    default_detail = "Credit sale amount exceeds available customer credit limit."


class CashierSessionRequiredError(SalesDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "register_session_required"
    default_detail = "An active cash register session is required for cash sales operations."

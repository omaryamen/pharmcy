"""Domain exception hierarchy for Enterprise Customer Sales Returns & Refund Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class CustomerReturnDomainError(APIException):
    """Base domain exception for customer return operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "customer_return_domain_error"
    default_detail = "A customer return domain error occurred."


class ExceedsReturnableQuantityError(CustomerReturnDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_returnable_quantity"
    default_detail = "Requested return quantity exceeds returnable quantity for this sales line."


class ExceedsRefundableAmountError(CustomerReturnDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_refundable_amount"
    default_detail = "Refund amount exceeds eligible accepted return value."


class InvalidReturnStateError(CustomerReturnDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_return_state"
    default_detail = "Customer return document is in an invalid state for this operation."


class ReturnApprovalSelfForbiddenError(CustomerReturnDomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "return_self_approval_forbidden"
    default_detail = "Customer return requester cannot approve their own return request."


class RefundAlreadyProcessedError(CustomerReturnDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "refund_already_processed"
    default_detail = "A refund has already been completed for this customer return."

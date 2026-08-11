"""Domain exception hierarchy for Enterprise Purchase Returns & Supplier Returns."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class PurchaseReturnDomainError(APIException):
    """Base domain exception for purchase return operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "purchase_return_domain_error"
    default_detail = "A purchase return error occurred."


class InvalidReturnStateError(PurchaseReturnDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_return_state"
    default_detail = "The purchase return is in an invalid state for this operation."


class ExceedsReturnableQuantityError(PurchaseReturnDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_returnable_quantity"
    default_detail = "Requested return quantity exceeds total received quantity or available stock."


class ReturnAlreadyDispatchedError(PurchaseReturnDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "already_dispatched"
    default_detail = "Purchase return has already been dispatched to supplier."


class CannotCancelDispatchedReturnError(PurchaseReturnDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cannot_cancel_dispatched"
    default_detail = "Cannot cancel a purchase return that has already been dispatched."


class ReturnSelfApprovalForbiddenError(PurchaseReturnDomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "self_approval_forbidden"
    default_detail = "Requester / Creator cannot approve their own Purchase Return."

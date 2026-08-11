"""Domain exception hierarchy for Enterprise Purchasing & Purchase Order Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class ProcurementDomainError(APIException):
    """Base domain exception for procurement operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "procurement_domain_error"
    default_detail = "A procurement error occurred."


class InvalidRequisitionStateError(ProcurementDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_requisition_state"
    default_detail = "The purchase requisition is in an invalid state for this operation."


class InvalidPurchaseOrderStateError(ProcurementDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_po_state"
    default_detail = "The purchase order is in an invalid state for this operation."


class InactiveSupplierError(ProcurementDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "inactive_supplier"
    default_detail = "The selected supplier is inactive, suspended, or blocked for procurement."


class InactiveMedicineError(ProcurementDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "inactive_medicine"
    default_detail = "The selected medicine is inactive or discontinued."


class RequisitionAlreadyConvertedError(ProcurementDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "requisition_already_converted"
    default_detail = "This requisition has already been converted to a Purchase Order."


class SelfApprovalForbiddenError(ProcurementDomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "self_approval_forbidden"
    default_detail = "Requester / Creator user cannot approve their own high-value Purchase Order."


class CannotCancelReceivedPOError(ProcurementDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cannot_cancel_received_po"
    default_detail = "Cannot cancel a Purchase Order that has already been fully or partially received."


class InvalidAmendmentError(ProcurementDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_amendment"
    default_detail = "Cannot amend critical fields of a Purchase Order that is already being received."

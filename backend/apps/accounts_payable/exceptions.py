"""Domain exception hierarchy for Enterprise Supplier Invoices & Accounts Payable Foundation."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class AccountsPayableDomainError(APIException):
    """Base domain exception for Accounts Payable operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "ap_domain_error"
    default_detail = "An accounts payable domain error occurred."


class DuplicateSupplierInvoiceError(AccountsPayableDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "duplicate_supplier_invoice"
    default_detail = "A supplier invoice with this invoice number already exists for this supplier."


class ThreeWayMatchError(AccountsPayableDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "three_way_match_failed"
    default_detail = "Three-way match failed between Purchase Order, Goods Receipt, and Invoice."


class InvalidInvoiceStateError(AccountsPayableDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_invoice_state"
    default_detail = "The supplier invoice is in an invalid state for this operation."


class ExceedsOutstandingBalanceError(AccountsPayableDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_outstanding_balance"
    default_detail = "Payment or credit amount exceeds total outstanding payable balance."


class PaymentSelfApprovalForbiddenError(AccountsPayableDomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "self_approval_forbidden"
    default_detail = "Creator cannot approve their own high-value Supplier Payment or Invoice."


class PaymentAlreadyReversedError(AccountsPayableDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "payment_already_reversed"
    default_detail = "This supplier payment has already been reversed."

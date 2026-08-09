"""Exceptions specific to Enterprise Customer Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError, ValidationFailedError


class CustomerNotFoundError(NotFoundError):
    code = "customer_not_found"
    message = "The requested customer record does not exist."


class CustomerStatusError(BusinessRuleViolation):
    code = "customer_status_invalid"
    message = "The operation cannot be performed for the customer in its current status."


class DuplicateCustomerCodeError(ConflictError):
    code = "duplicate_customer_code"
    message = "A customer with this code already exists in this tenant."


class DuplicateCustomerNumberError(ConflictError):
    code = "duplicate_customer_number"
    message = "A customer with this customer number already exists in this tenant."


class CustomerDeleteForbiddenError(BusinessRuleViolation):
    code = "customer_delete_forbidden"
    message = "Cannot delete customer because active sales, invoices, prescriptions, or ledger entries exist."


class InvalidCreditLimitError(ValidationFailedError):
    code = "invalid_credit_limit"
    message = "Credit limit cannot be negative."


class CustomerAddressNotFoundError(NotFoundError):
    code = "customer_address_not_found"
    message = "The requested customer address record does not exist."


class CustomerMedicalProfileNotFoundError(NotFoundError):
    code = "customer_medical_profile_not_found"
    message = "The requested customer medical profile does not exist."

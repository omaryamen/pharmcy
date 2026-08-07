"""Exceptions specific to Enterprise Supplier Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class SupplierNotFoundError(NotFoundError):
    code = "supplier_not_found"
    message = "The requested supplier record does not exist."


class SupplierStatusError(BusinessRuleViolation):
    code = "supplier_status_invalid"
    message = "The operation cannot be performed for the supplier in its current status."


class DuplicateSupplierCodeError(ConflictError):
    code = "duplicate_supplier_code"
    message = "A supplier with this code already exists in this tenant."


class DuplicateSupplierLegalNameError(ConflictError):
    code = "duplicate_supplier_legal_name"
    message = "A supplier with this legal name already exists in this tenant."


class SupplierDeleteForbiddenError(BusinessRuleViolation):
    code = "supplier_delete_forbidden"
    message = "Cannot delete supplier because active purchase orders, invoices, payments, or inventory transactions exist."

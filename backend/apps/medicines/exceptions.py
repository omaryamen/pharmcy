"""Exceptions specific to Enterprise Medicine Master Data."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class MedicineNotFoundError(NotFoundError):
    code = "medicine_not_found"
    message = "The requested medicine master entry does not exist."


class MedicineStatusError(BusinessRuleViolation):
    code = "medicine_status_invalid"
    message = "The operation cannot be performed for the medicine in its current status."


class DuplicateMedicineCodeError(ConflictError):
    code = "duplicate_medicine_code"
    message = "A medicine with this code already exists in this tenant."


class DuplicateBarcodeError(ConflictError):
    code = "duplicate_medicine_barcode"
    message = "A medicine with this barcode already exists in this tenant."


class DuplicateSKUError(ConflictError):
    code = "duplicate_medicine_sku"
    message = "A medicine with this SKU already exists in this tenant."


class MedicineDeleteForbiddenError(BusinessRuleViolation):
    code = "medicine_delete_forbidden"
    message = "Cannot delete medicine master record because it is referenced in inventory or transactions."

"""Exceptions specific to Enterprise Pharmaceutical Reference Data."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class ReferenceNotFoundError(NotFoundError):
    code = "reference_not_found"
    message = "The requested reference data item does not exist."


class DuplicateReferenceCodeError(ConflictError):
    code = "duplicate_reference_code"
    message = "A reference item with this code already exists."


class CategoryParentLoopError(BusinessRuleViolation):
    code = "category_parent_loop"
    message = "A category cannot be set as a child of itself or one of its descendants."

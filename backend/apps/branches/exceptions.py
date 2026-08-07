"""Exceptions specific to Branch Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class BranchNotFoundError(NotFoundError):
    code = "branch_not_found"
    message = "The requested branch does not exist."


class BranchStatusError(BusinessRuleViolation):
    code = "branch_status_invalid"
    message = "The operation cannot be performed for the branch in its current status."


class DuplicateBranchCodeError(ConflictError):
    code = "duplicate_branch_code"
    message = "A branch with this code or name already exists in this company."


class BranchDeleteForbiddenError(BusinessRuleViolation):
    code = "branch_delete_forbidden"
    message = "Cannot delete branch because it contains active inventory, sales, purchases, or employees."


class CompanyMismatchError(BusinessRuleViolation):
    code = "company_tenant_mismatch"
    message = "The specified company does not belong to the current tenant."

"""Exceptions specific to Company Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class CompanyNotFoundError(NotFoundError):
    code = "company_not_found"
    message = "The requested company does not exist."


class CompanyStatusError(BusinessRuleViolation):
    code = "company_status_invalid"
    message = "The operation cannot be performed for the company in its current status."


class DuplicateCompanyNameError(ConflictError):
    code = "duplicate_company_name"
    message = "A company with this name, code, or slug already exists for this tenant."


class CompanyDeleteForbiddenError(BusinessRuleViolation):
    code = "company_delete_forbidden"
    message = "Cannot delete company because it contains active branches, employees, warehouses, or transactions."

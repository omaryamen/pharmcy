"""Exceptions specific to Enterprise User Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    code = "user_not_found"
    message = "The requested user or employee profile does not exist."


class UserStatusError(BusinessRuleViolation):
    code = "user_status_invalid"
    message = "The operation cannot be performed for the user in its current status."


class DuplicateUserEmailError(ConflictError):
    code = "duplicate_user_email"
    message = "A user with this email or username already exists in this tenant."


class UserDeleteForbiddenError(BusinessRuleViolation):
    code = "user_delete_forbidden"
    message = "Cannot delete user because they have active sales, purchases, prescriptions, or inventory records."


class BranchCompanyMismatchError(BusinessRuleViolation):
    code = "user_branch_company_mismatch"
    message = "Assigned branch does not belong to the selected company or tenant."

"""Domain exception hierarchy for Enterprise Expense & Operating Cost Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class ExpenseException(APIException):
    """Base exception for expense operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "expense_error"
    default_detail = "An expense management error occurred."


class InvalidExpenseStatusError(ExpenseException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_expense_status"
    default_detail = "Expense record is not in a valid status for this workflow action."


class ExpenseAlreadyPostedError(ExpenseException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "expense_already_posted"
    default_detail = "Expense record has already been posted to the General Ledger and cannot be modified."


class DuplicateRecurringExpenseError(ExpenseException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "duplicate_recurring_expense"
    default_detail = "A recurring expense for this period has already been generated."


class ClosedPeriodPostingError(ExpenseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "closed_period_posting"
    default_detail = "Cannot post expense into a CLOSED or LOCKED accounting period."

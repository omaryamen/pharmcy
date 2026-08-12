"""Domain exception hierarchy for Enterprise General Ledger & Double-Entry Accounting."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class GLException(APIException):
    """Base exception for General Ledger operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "gl_operation_error"
    default_detail = "A General Ledger accounting error occurred."


class UnbalancedJournalError(GLException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "unbalanced_journal"
    default_detail = "Double-entry violation: Total debits must equal total credits."


class PeriodClosedError(GLException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "period_closed"
    default_detail = "Accounting period is closed or locked. Postings are prohibited."


class ControlAccountPostingForbiddenError(GLException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "control_account_posting_forbidden"
    default_detail = "Direct journal posting to non-postable summary/control parent accounts is forbidden."


class JournalAlreadyPostedError(GLException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "journal_already_posted"
    default_detail = "Journal entry is already posted and immutable."


class InvalidJournalStateError(GLException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_journal_state"
    default_detail = "Journal entry is in an invalid status for this operation."

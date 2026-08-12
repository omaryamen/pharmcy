"""Domain exception hierarchy for Enterprise Cash, Bank & Financial Reconciliation."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class CashAndBankException(APIException):
    """Base exception for cash and bank operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cash_bank_error"
    default_detail = "A cash, bank or treasury management error occurred."


class InsufficientCashBalanceError(CashAndBankException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "insufficient_cash_balance"
    default_detail = "Insufficient cash account balance to execute this disbursement/transfer."


class InsufficientBankBalanceError(CashAndBankException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "insufficient_bank_balance"
    default_detail = "Insufficient bank account balance to execute this withdrawal."


class DuplicateBankImportError(CashAndBankException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "duplicate_bank_import"
    default_detail = "Bank transaction with matching external reference or import hash has already been imported."


class CashSessionAlreadyClosedError(CashAndBankException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "cash_session_already_closed"
    default_detail = "POS cash session is already closed and reconciled."

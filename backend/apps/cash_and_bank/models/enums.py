"""Domain choices & enums for Enterprise Cash, Bank & Financial Reconciliation."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CashMovementType(models.TextChoices):
    SALE = "sale", _("POS Cash Sale")
    REFUND = "refund", _("POS Cash Refund")
    CUSTOMER_PAYMENT = "customer_payment", _("Customer AR Cash Payment")
    CUSTOMER_RECEIPT = "customer_receipt", _("Customer Receipt")
    SUPPLIER_PAYMENT = "supplier_payment", _("Supplier AP Cash Payment")
    DEPOSIT = "deposit", _("Cash Deposit to Bank")
    WITHDRAWAL = "withdrawal", _("Cash Withdrawal from Bank")
    TRANSFER_IN = "transfer_in", _("Cash Transfer In")
    TRANSFER_OUT = "transfer_out", _("Cash Transfer Out")
    ADJUSTMENT = "adjustment", _("Cash Balance Adjustment")
    OPENING_BALANCE = "opening_balance", _("Opening Float Balance")
    CLOSING_ADJUSTMENT = "closing_adjustment", _("Till Closing Variance Adjustment")
    OTHER = "other", _("Other Cash Flow")


class OperationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PENDING_APPROVAL = "pending_approval", _("Pending Manager Approval")
    APPROVED = "approved", _("Approved")
    POSTED = "posted", _("Posted")
    CANCELLED = "cancelled", _("Cancelled")
    REJECTED = "rejected", _("Rejected")


class BankTransactionType(models.TextChoices):
    DEPOSIT = "deposit", _("Bank Deposit")
    WITHDRAWAL = "withdrawal", _("Bank Withdrawal")
    TRANSFER = "transfer", _("Bank Transfer")
    FEE = "fee", _("Bank Fee / Charge")
    INTEREST = "interest", _("Interest Income / Expense")
    REFUND = "refund", _("Bank Refund")
    PAYMENT = "payment", _("Bank Payment")
    OTHER = "other", _("Other Bank Transaction")


class BankReconciliationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Reconciliation")
    IN_PROGRESS = "in_progress", _("In Progress")
    RECONCILED = "reconciled", _("Fully Reconciled")
    DISCREPANCY = "discrepancy", _("Discrepancy Unresolved")
    CLOSED = "closed", _("Closed Period")


class ReconciliationMatchStatus(models.TextChoices):
    UNMATCHED = "unmatched", _("Unmatched")
    PARTIALLY_MATCHED = "partially_matched", _("Partially Matched")
    MATCHED = "matched", _("Matched")
    IGNORED = "ignored", _("Ignored / Excluded")


class ExceptionType(models.TextChoices):
    MISSING_BOOK_ENTRY = "missing_book_entry", _("Missing Book Entry")
    MISSING_EXTERNAL_ENTRY = "missing_external_entry", _("Missing Bank Statement Entry")
    AMOUNT_MISMATCH = "amount_mismatch", _("Amount Mismatch")
    DUPLICATE = "duplicate", _("Duplicate Bank Transaction")
    UNKNOWN_TRANSACTION = "unknown_transaction", _("Unknown Transaction")
    TIMING_DIFFERENCE = "timing_difference", _("Timing Difference")
    BANK_FEE = "bank_fee", _("Unrecorded Bank Fee")
    INTEREST = "interest", _("Unrecorded Interest")
    FX_DIFFERENCE = "fx_difference", _("Exchange Rate Difference")
    OTHER = "other", _("Other Discrepancy")


class ExceptionStatus(models.TextChoices):
    OPEN = "open", _("Open Exception")
    UNDER_REVIEW = "under_review", _("Under Review")
    RESOLVED = "resolved", _("Resolved")
    IGNORED = "ignored", _("Ignored")


class VarianceType(models.TextChoices):
    SHORTAGE = "shortage", _("Cash Shortage (Deficit)")
    OVERAGE = "overage", _("Cash Overage (Surplus)")

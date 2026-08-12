"""Domain choices & enums for Enterprise Expense & Operating Cost Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    PENDING_APPROVAL = "pending_approval", _("Pending Manager Approval")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Paid")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")
    DISPUTED = "disputed", _("Disputed")


class RequestStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Request")
    SUBMITTED = "submitted", _("Submitted")
    UNDER_REVIEW = "under_review", _("Under Review")
    APPROVED = "approved", _("Approved Pre-Request")
    REJECTED = "rejected", _("Rejected Request")
    CANCELLED = "cancelled", _("Cancelled Request")
    CONVERTED_TO_EXPENSE = "converted_to_expense", _("Converted to Official Expense")


class PaymentMethod(models.TextChoices):
    CASH = "cash", _("Immediate Cash Settlement")
    BANK = "bank", _("Immediate Bank Transfer")
    SUPPLIER_PAYABLE = "supplier_payable", _("Supplier Accounts Payable")
    EMPLOYEE_REIMBURSEMENT = "employee_reimbursement", _("Employee Expense Reimbursement")
    PETTY_CASH = "petty_cash", _("Petty Cash Fund")


class RecurringFrequency(models.TextChoices):
    DAILY = "daily", _("Daily")
    WEEKLY = "weekly", _("Weekly")
    MONTHLY = "monthly", _("Monthly")
    QUARTERLY = "quarterly", _("Quarterly")
    SEMI_ANNUAL = "semi_annual", _("Semi-Annual")
    YEARLY = "yearly", _("Yearly")
    CUSTOM = "custom", _("Custom Schedule")


class ReimbursementStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Claim")
    SUBMITTED = "submitted", _("Submitted")
    APPROVED = "approved", _("Approved Claim")
    REJECTED = "rejected", _("Rejected Claim")
    PARTIALLY_REIMBURSED = "partially_reimbursed", _("Partially Reimbursed")
    REIMBURSED = "reimbursed", _("Fully Reimbursed")
    CANCELLED = "cancelled", _("Cancelled")

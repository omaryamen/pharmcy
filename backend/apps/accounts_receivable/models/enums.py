"""Domain choices & enums for Enterprise Customer Accounts Receivable (AR)."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ARStatus(models.TextChoices):
    OPEN = "open", _("Open Receivable")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Fully Paid")
    OVERDUE = "overdue", _("Overdue")
    DISPUTED = "disputed", _("Disputed")
    CREDIT = "credit", _("Credit Balance")
    WRITTEN_OFF = "written_off", _("Written Off")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")


class ARPaymentStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Payment")
    POSTED = "posted", _("Posted Payment")
    PARTIALLY_ALLOCATED = "partially_allocated", _("Partially Allocated")
    FULLY_ALLOCATED = "fully_allocated", _("Fully Allocated")
    REVERSED = "reversed", _("Reversed")


class ARPaymentMethod(models.TextChoices):
    CASH = "cash", _("Cash Payment")
    BANK_TRANSFER = "bank_transfer", _("Bank Wire Transfer")
    CARD = "card", _("Credit / Debit Card")
    MOBILE_WALLET = "mobile_wallet", _("Mobile Wallet")
    ONLINE_PAYMENT = "online_payment", _("Online Payment Gateway")
    OTHER = "other", _("Other Payment Method")


class OverpaymentPolicy(models.TextChoices):
    REJECT = "reject", _("Reject Overpayment")
    ALLOW_AS_CUSTOMER_CREDIT = "allow_as_customer_credit", _("Allow as Customer Store Credit")
    ALLOW_WITH_APPROVAL = "allow_with_approval", _("Allow with Manager Approval")


class ARAdjustmentType(models.TextChoices):
    DEBIT_ADJUSTMENT = "debit_adjustment", _("Debit Adjustment (Increase Receivable)")
    CREDIT_ADJUSTMENT = "credit_adjustment", _("Credit Adjustment (Decrease Receivable)")
    WRITE_OFF = "write_off", _("Bad Debt Write-Off")
    CORRECTION = "correction", _("Accounting Correction")
    OTHER = "other", _("Other Adjustment")


class ARAdjustmentStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Adjustment")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    POSTED = "posted", _("Posted")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")


class DisputeReason(models.TextChoices):
    WRONG_AMOUNT = "wrong_amount", _("Incorrect Invoiced Amount")
    DUPLICATE_CHARGE = "duplicate_charge", _("Duplicate Invoiced Charge")
    RETURN_PENDING = "return_pending", _("Pending Return / Credit Note")
    PAYMENT_NOT_RECORDED = "payment_not_recorded", _("Unrecorded Payment")
    PRICE_DISPUTE = "price_dispute", _("Unit Price Dispute")
    OTHER = "other", _("Other Dispute Reason")


class DisputeStatus(models.TextChoices):
    OPEN = "open", _("Dispute Open")
    UNDER_REVIEW = "under_review", _("Under Financial Review")
    RESOLVED_CREDIT = "resolved_credit", _("Resolved with Credit Adjustment")
    RESOLVED_REJECTED = "resolved_rejected", _("Dispute Rejected")
    CANCELLED = "cancelled", _("Cancelled")

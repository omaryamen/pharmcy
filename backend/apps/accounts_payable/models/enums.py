"""Domain choices & enums for Enterprise Supplier Invoices & Accounts Payable Foundation."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    RECEIVED = "received", _("Received")
    UNDER_REVIEW = "under_review", _("Under Review")
    VERIFIED = "verified", _("Verified")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    POSTED = "posted", _("Posted to Accounts Payable")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Fully Paid")
    OVERDUE = "overdue", _("Overdue")
    DISPUTED = "disputed", _("Disputed")
    CANCELLED = "cancelled", _("Cancelled")
    VOIDED = "voided", _("Voided")


class MatchStatus(models.TextChoices):
    NOT_MATCHED = "not_matched", _("Not Matched")
    MATCHED = "matched", _("Matched (Three-Way Match OK)")
    PARTIAL_MATCH = "partial_match", _("Partial Match")
    PRICE_VARIANCE = "price_variance", _("Price Variance Identified")
    QUANTITY_VARIANCE = "quantity_variance", _("Quantity Variance Identified")
    TAX_VARIANCE = "tax_variance", _("Tax Variance Identified")
    SUPPLIER_MISMATCH = "supplier_mismatch", _("Supplier Mismatch")
    RECEIPT_MISSING = "receipt_missing", _("Goods Receipt Missing")
    DISPUTED = "disputed", _("Disputed")
    APPROVED = "approved", _("Approved Match Exception")


class APStatus(models.TextChoices):
    OPEN = "open", _("Open Payable")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Paid")
    OVERDUE = "overdue", _("Overdue")
    DISPUTED = "disputed", _("Disputed")
    CANCELLED = "cancelled", _("Cancelled")
    WRITTEN_OFF = "written_off", _("Written Off")


class PaymentTerms(models.TextChoices):
    CASH = "cash", _("Cash on Delivery / Instant")
    NET_7 = "net_7", _("Net 7 Days")
    NET_15 = "net_15", _("Net 15 Days")
    NET_30 = "net_30", _("Net 30 Days")
    NET_45 = "net_45", _("Net 45 Days")
    NET_60 = "net_60", _("Net 60 Days")
    NET_90 = "net_90", _("Net 90 Days")
    CUSTOM = "custom", _("Custom Due Date")


class PaymentMethod(models.TextChoices):
    CASH = "cash", _("Cash")
    BANK_TRANSFER = "bank_transfer", _("Bank Electronic Transfer / Wire")
    CHECK = "check", _("Bank Check")
    CARD = "card", _("Corporate Credit / Debit Card")
    ONLINE_PAYMENT = "online_payment", _("Online Payment Portal")
    OTHER = "other", _("Other Payment Method")


class PaymentStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    POSTED = "posted", _("Posted / Executed")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")


class DisputeReason(models.TextChoices):
    PRICE_VARIANCE = "price_variance", _("Price Variance vs PO")
    QUANTITY_VARIANCE = "quantity_variance", _("Quantity Variance vs Receipt")
    DAMAGED_GOODS = "damaged_goods", _("Damaged Goods Billed")
    MISSING_GOODS = "missing_goods", _("Missing / Shorted Goods Billed")
    WRONG_ITEM = "wrong_item", _("Wrong Product Invoiced")
    WRONG_BATCH = "wrong_batch", _("Wrong Batch Invoiced")
    TAX_ERROR = "tax_error", _("Tax Rate / Tax Calculation Error")
    DUPLICATE_INVOICE = "duplicate_invoice", _("Duplicate Bill Invoiced")
    OTHER = "other", _("Other Dispute Reason")


class DisputeStatus(models.TextChoices):
    PENDING = "pending", _("Pending Review")
    REVIEWED = "reviewed", _("Under Review")
    RESOLVED = "resolved", _("Resolved")
    REJECTED = "rejected", _("Rejected")

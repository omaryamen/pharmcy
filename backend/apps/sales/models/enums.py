"""Domain choices & enums for Enterprise POS & Sales Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SalesStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Sale")
    HELD = "held", _("Held Sale / Cart")
    PENDING_PAYMENT = "pending_payment", _("Pending Payment")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Paid")
    CREDIT = "credit", _("Customer Credit Sale")
    COMPLETED = "completed", _("Completed Sale")
    CANCELLED = "cancelled", _("Cancelled")
    VOIDED = "voided", _("Voided")
    REFUNDED = "refunded", _("Fully Refunded")
    PARTIALLY_REFUNDED = "partially_refunded", _("Partially Refunded")


class InvoicePaymentStatus(models.TextChoices):
    UNPAID = "unpaid", _("Unpaid")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAID = "paid", _("Fully Paid")
    OVERPAID = "overpaid", _("Overpaid")
    CREDIT = "credit", _("Customer Account Balance Credit")


class SalesPaymentStatus(models.TextChoices):
    POSTED = "posted", _("Posted")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")


class SalesPaymentMethod(models.TextChoices):
    CASH = "cash", _("Cash Tender")
    CARD = "card", _("Debit / Credit Card Terminal")
    BANK_TRANSFER = "bank_transfer", _("Bank Electronic Transfer")
    MOBILE_WALLET = "mobile_wallet", _("Mobile Payment Wallet")
    ONLINE_PAYMENT = "online_payment", _("Online Payment Gateway")
    CUSTOMER_CREDIT = "customer_credit", _("Customer Credit Account")
    MIXED_PAYMENT = "mixed_payment", _("Mixed / Split Payment")
    OTHER = "other", _("Other Payment Method")


class BatchAllocationStrategy(models.TextChoices):
    FEFO = "fefo", _("First Expiry, First Out (FEFO)")
    FIFO = "fifo", _("First In, First Out (FIFO)")
    MANUAL = "manual", _("Manual Batch Selection")


class RegisterStatus(models.TextChoices):
    CLOSED = "closed", _("Closed")
    OPEN = "open", _("Open / Operational")
    MAINTENANCE = "maintenance", _("Maintenance")


class SessionStatus(models.TextChoices):
    OPEN = "open", _("Session Open")
    CLOSED = "closed", _("Session Closed")
    RECONCILED = "reconciled", _("Reconciled & Audited")

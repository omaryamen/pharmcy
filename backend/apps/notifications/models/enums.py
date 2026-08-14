"""Domain choices & enums for Enterprise Notifications & Automation Engine."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EventTypeChoices(models.TextChoices):
    # User & Security
    USER_CREATED = "user.created", _("User Created")
    USER_LOCKED = "user.locked", _("User Account Locked")
    SECURITY_EVENT = "security.event", _("Security Event")

    # Inventory & Alerts
    MEDICINE_LOW_STOCK = "inventory.low_stock", _("Medicine Low Stock")
    MEDICINE_OUT_OF_STOCK = "inventory.out_of_stock", _("Medicine Out of Stock")
    MEDICINE_NEAR_EXPIRY = "inventory.near_expiry", _("Medicine Near Expiry")
    MEDICINE_EXPIRED = "inventory.expired", _("Medicine Expired")
    BATCH_RECALLED = "inventory.batch_recalled", _("Pharmaceutical Batch Recalled")
    STOCK_ADJUSTED = "inventory.stock_adjusted", _("Stock Adjusted")
    STOCK_TRANSFERRED = "inventory.stock_transferred", _("Stock Transferred")

    # Purchasing & AP
    PURCHASE_CREATED = "procurement.purchase_created", _("Purchase Order Created")
    PURCHASE_RECEIVED = "goods_receipt.received", _("Goods Receipt Received")
    SUPPLIER_INVOICE_CREATED = "accounts_payable.invoice_created", _("Supplier Invoice Created")
    SUPPLIER_PAYMENT_DUE = "accounts_payable.payment_due", _("Supplier Payment Due")

    # Sales & POS & AR
    SALES_COMPLETED = "sales.completed", _("Sales Completed")
    SALE_RETURNED = "sales.returned", _("Sale Returned")
    REFUND_CREATED = "sales.refund_created", _("Refund Created")
    CUSTOMER_PAYMENT_OVERDUE = "accounts_receivable.payment_overdue", _("Customer Payment Overdue")

    # Prescriptions
    PRESCRIPTION_CREATED = "prescription.created", _("Prescription Created")
    PRESCRIPTION_VERIFIED = "prescription.verified", _("Prescription Verified")
    PRESCRIPTION_DISPENSED = "prescription.dispensed", _("Prescription Dispensed")

    # Treasury & Expenses
    CASH_VARIANCE_DETECTED = "cash.variance_detected", _("Cash Shift Variance Detected")
    BANK_RECONCILIATION_DIFFERENCE = "bank.reconciliation_difference", _("Bank Reconciliation Difference")
    EXPENSE_APPROVAL_REQUIRED = "expenses.approval_required", _("Expense Approval Required")
    EXPENSE_APPROVED = "expenses.approved", _("Expense Approved")
    BUDGET_THRESHOLD_REACHED = "expenses.budget_threshold_reached", _("Budget Threshold Reached")

    # System
    SYSTEM_ERROR = "system.error", _("System Error Alert")


class EventStatus(models.TextChoices):
    PENDING = "pending", _("Pending Processing")
    PROCESSING = "processing", _("Processing")
    PROCESSED = "processed", _("Processed Successfully")
    FAILED = "failed", _("Processing Failed")
    DEAD_LETTER = "dead_letter", _("Moved to Dead Letter Queue")


class NotificationPriority(models.TextChoices):
    LOW = "low", _("Low Priority")
    NORMAL = "normal", _("Normal Priority")
    HIGH = "high", _("High Priority")
    URGENT = "urgent", _("Urgent Priority")
    CRITICAL = "critical", _("Critical Priority")


class NotificationStatus(models.TextChoices):
    PENDING = "pending", _("Pending Delivery")
    SENT = "sent", _("Sent")
    DELIVERED = "delivered", _("Delivered")
    READ = "read", _("Read by Recipient")
    FAILED = "failed", _("Delivery Failed")
    DISMISSED = "dismissed", _("Dismissed by Recipient")
    EXPIRED = "expired", _("Expired")
    CANCELLED = "cancelled", _("Cancelled")


class NotificationChannel(models.TextChoices):
    IN_APP = "in_app", _("In-App Notification")
    EMAIL = "email", _("Email Notification")
    SMS = "sms", _("SMS Text Message")
    PUSH = "push", _("Mobile/Browser Push")
    WEBHOOK = "webhook", _("Webhook HTTP POST")
    WHATSAPP = "whatsapp", _("WhatsApp Message")


class DigestFrequency(models.TextChoices):
    IMMEDIATE = "immediate", _("Immediate Delivery")
    HOURLY = "hourly", _("Hourly Digest")
    DAILY = "daily", _("Daily Digest Summary")
    WEEKLY = "weekly", _("Weekly Digest Summary")

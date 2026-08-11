"""Domain choices & enums for Enterprise Customer Sales Returns & Refund Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReturnStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Return Request")
    REQUESTED = "requested", _("Requested / Submitted")
    PENDING_APPROVAL = "pending_approval", _("Pending Manager Approval")
    APPROVED = "approved", _("Approved")
    INSPECTION = "inspection", _("Under Quality Inspection")
    PARTIALLY_ACCEPTED = "partially_accepted", _("Partially Accepted")
    ACCEPTED = "accepted", _("Fully Accepted")
    REJECTED = "rejected", _("Rejected")
    REFUND_PENDING = "refund_pending", _("Refund Pending Processing")
    REFUNDED = "refunded", _("Refunded to Customer")
    STORE_CREDIT_ISSUED = "store_credit_issued", _("Store Credit Issued")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")
    CLOSED = "closed", _("Closed")


class ReturnReason(models.TextChoices):
    WRONG_ITEM = "wrong_item", _("Wrong Medicine / Item Dispensed")
    WRONG_QUANTITY = "wrong_quantity", _("Wrong Quantity Dispensed")
    DAMAGED = "damaged", _("Damaged Product")
    DEFECTIVE = "defective", _("Defective Product")
    EXPIRED = "expired", _("Expired Medicine")
    NEAR_EXPIRY = "near_expiry", _("Near Expiry Date")
    ALLERGIC_REACTION = "allergic_reaction", _("Adverse Effect / Allergic Reaction")
    CUSTOMER_CHANGED_MIND = "customer_changed_mind", _("Customer Changed Mind")
    QUALITY_ISSUE = "quality_issue", _("Quality Defect")
    PACKAGING_DAMAGE = "packaging_damage", _("Damaged Packaging")
    PRESCRIPTION_ERROR = "prescription_error", _("Prescription Change / Error")
    DUPLICATE_PURCHASE = "duplicate_purchase", _("Duplicate Purchase")
    OTHER = "other", _("Other Reason")


class ProductCondition(models.TextChoices):
    SEALED = "sealed", _("Sealed / Original Condition")
    OPENED = "opened", _("Opened Outer Packaging")
    DAMAGED = "damaged", _("Physically Damaged")
    EXPIRED = "expired", _("Expired Date")
    REFRIGERATED = "refrigerated", _("Cold Chain Refrigerated")
    TEMPERATURE_DAMAGED = "temperature_damaged", _("Temperature Excursion / Damaged Cold Chain")
    QUARANTINED = "quarantined", _("Quarantined Stock")
    RECALLED = "recalled", _("Pharmacovigilance Recalled Batch")
    UNKNOWN = "unknown", _("Unknown Condition")


class InspectionResult(models.TextChoices):
    ACCEPTED = "accepted", _("Accepted for Normal Resale Stock")
    REJECTED = "rejected", _("Rejected Return")
    QUARANTINED = "quarantined", _("Sent to Quarantine Stock")
    DAMAGED = "damaged", _("Sent to Damaged Stock")
    EXPIRED = "expired", _("Expired Stock Write-Off")
    RECALLED = "recalled", _("Batch Recall Hold")


class RefundMethod(models.TextChoices):
    CASH = "cash", _("Cash Refund")
    CARD = "card", _("Debit / Credit Card Refund")
    BANK_TRANSFER = "bank_transfer", _("Bank Electronic Transfer")
    MOBILE_WALLET = "mobile_wallet", _("Mobile Wallet Refund")
    ORIGINAL_PAYMENT_METHOD = "original_payment_method", _("Original Payment Method")
    STORE_CREDIT = "store_credit", _("Customer Account Store Credit")
    OTHER = "other", _("Other Refund Method")


class RefundStatus(models.TextChoices):
    PENDING = "pending", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    PROCESSING = "processing", _("Processing")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")

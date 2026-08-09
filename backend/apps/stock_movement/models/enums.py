"""Enumerations for Enterprise Stock Movement Engine."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MovementType(models.TextChoices):
    OPENING_BALANCE = "opening_balance", _("Opening Balance")
    RECEIPT = "receipt", _("Stock Receipt")
    ISSUE = "issue", _("Stock Issue")
    SALE = "sale", _("POS / Sales Issue")
    SALE_RETURN = "sale_return", _("Sales Return")
    PURCHASE_RETURN = "purchase_return", _("Purchase Return")
    TRANSFER_OUT = "transfer_out", _("Transfer Out")
    TRANSFER_IN = "transfer_in", _("Transfer In")
    ADJUSTMENT_IN = "adjustment_in", _("Adjustment Increase (+)")
    ADJUSTMENT_OUT = "adjustment_out", _("Adjustment Decrease (-)")
    DAMAGE = "damage", _("Damage Movement")
    EXPIRY = "expiry", _("Expiry Movement")
    QUARANTINE = "quarantine", _("Move to Quarantine")
    QUARANTINE_RELEASE = "quarantine_release", _("Release from Quarantine")
    RESERVATION = "reservation", _("Stock Reservation")
    RESERVATION_RELEASE = "reservation_release", _("Reservation Release")
    CORRECTION = "correction", _("Correction Movement")
    RECALL = "recall", _("Batch Recall Movement")
    OTHER = "other", _("Other Movement")


class MovementStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    PROCESSING = "processing", _("Processing")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")
    FAILED = "failed", _("Failed")


class ReferenceType(models.TextChoices):
    PURCHASE_ORDER = "purchase_order", _("Purchase Order")
    GOODS_RECEIPT = "goods_receipt", _("Goods Receipt Note")
    SALES_INVOICE = "sales_invoice", _("Sales Invoice")
    SALES_RETURN = "sales_return", _("Sales Return Document")
    TRANSFER_REQUEST = "transfer_request", _("Stock Transfer Request")
    STOCK_COUNT = "stock_count", _("Physical Stock Count Sheet")
    ADJUSTMENT = "adjustment", _("Stock Adjustment Document")
    PRESCRIPTION = "prescription", _("Medical Prescription")
    MANUAL = "manual", _("Manual User Entry")
    OTHER = "other", _("Other Reference Document")

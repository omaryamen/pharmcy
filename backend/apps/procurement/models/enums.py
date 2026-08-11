"""Domain choices & enums for Enterprise Purchasing & Purchase Order Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class RequisitionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    UNDER_REVIEW = "under_review", _("Under Review")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")
    CONVERTED_TO_PO = "converted_to_po", _("Converted to PO")


class PurchaseOrderStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    SENT_TO_SUPPLIER = "sent_to_supplier", _("Sent to Supplier")
    ACKNOWLEDGED = "acknowledged", _("Acknowledged by Supplier")
    PARTIALLY_RECEIVED = "partially_received", _("Partially Received")
    FULLY_RECEIVED = "fully_received", _("Fully Received")
    CANCELLED = "cancelled", _("Cancelled")
    CLOSED = "closed", _("Closed")
    REJECTED = "rejected", _("Rejected")
    EXPIRED = "expired", _("Expired")


class ProcurementPriority(models.TextChoices):
    LOW = "low", _("Low Priority")
    NORMAL = "normal", _("Normal Priority")
    HIGH = "high", _("High Priority")
    URGENT = "urgent", _("Urgent Priority")
    EMERGENCY = "emergency", _("Emergency Purchase")


class ProcurementReason(models.TextChoices):
    LOW_STOCK = "low_stock", _("Low Stock Replenishment")
    OUT_OF_STOCK = "out_of_stock", _("Out of Stock Urgent Need")
    EXPIRY_REPLACEMENT = "expiry_replacement", _("Expiry Batch Replacement")
    NEW_PRODUCT = "new_product", _("New Product Introduction")
    REGULAR_REPLENISHMENT = "regular_replenishment", _("Regular Replenishment Cycle")
    CUSTOMER_REQUEST = "customer_request", _("Customer Special Request")
    EMERGENCY = "emergency", _("Emergency Supply Request")
    MANUAL = "manual", _("Manual Purchasing Order")
    OTHER = "other", _("Other Reason")

"""Domain choices & enums for Enterprise Purchase Returns & Supplier Returns."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReturnStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    PICKING = "picking", _("Picking in Progress")
    READY_FOR_DISPATCH = "ready_for_dispatch", _("Ready for Dispatch")
    DISPATCHED = "dispatched", _("Dispatched to Supplier")
    IN_TRANSIT = "in_transit", _("In Transit")
    PARTIALLY_ACCEPTED = "partially_accepted", _("Partially Accepted by Supplier")
    ACCEPTED = "accepted", _("Fully Accepted by Supplier")
    REJECTED = "rejected", _("Rejected by Supplier")
    CANCELLED = "cancelled", _("Cancelled")
    DISCREPANCY = "discrepancy", _("Discrepancy Identified")
    CLOSED = "closed", _("Closed")
    REVERSED = "reversed", _("Reversed")


class ReturnReason(models.TextChoices):
    DAMAGED = "damaged", _("Damaged Product")
    EXPIRED = "expired", _("Expired Product")
    NEAR_EXPIRY = "near_expiry", _("Near Expiry Short Shelf Life")
    WRONG_ITEM = "wrong_item", _("Wrong Medicine Delivered")
    WRONG_BATCH = "wrong_batch", _("Wrong Batch Delivered")
    WRONG_QUANTITY = "wrong_quantity", _("Wrong Quantity / Over-shipment")
    QUALITY_DEFECT = "quality_defect", _("Quality Defect / Manufacturing Defect")
    RECALLED = "recalled", _("Batch Recall Notice")
    TEMPERATURE_EXCURSION = "temperature_excursion", _("Cold Chain Temperature Excursion")
    SUPPLIER_ERROR = "supplier_error", _("Supplier Dispatch Error")
    PURCHASE_ERROR = "purchase_error", _("Internal Ordering Error")
    CUSTOMER_RETURN = "customer_return", _("Customer Return Back to Supplier")
    EXCESS_STOCK = "excess_stock", _("Excess Stock Return")
    OTHER = "other", _("Other Return Reason")


class ProductCondition(models.TextChoices):
    SEALED = "sealed", _("Factory Sealed Original Packaging")
    OPENED = "opened", _("Opened Box / Outer Seal Broken")
    DAMAGED = "damaged", _("Visually Damaged / Leaking")
    EXPIRED = "expired", _("Expired")
    QUARANTINED = "quarantined", _("Quarantined Batch")
    RECALLED = "recalled", _("Official Recall Notice")
    TEMPERATURE_DAMAGED = "temperature_damaged", _("Heat / Cold Excursion Damaged")
    OTHER = "other", _("Other Condition")


class DiscrepancyReason(models.TextChoices):
    SHORTAGE = "shortage", _("Supplier Quantity Shortage")
    OVERAGE = "overage", _("Supplier Quantity Overage")
    DAMAGE = "damage", _("Damaged in Transport to Supplier")
    WRONG_ITEM = "wrong_item", _("Wrong Item Claimed by Supplier")
    WRONG_BATCH = "wrong_batch", _("Wrong Batch Claimed by Supplier")
    WRONG_QUANTITY = "wrong_quantity", _("Disputed Quantity Count")
    OTHER = "other", _("Other Discrepancy Reason")


class CreditNoteStatus(models.TextChoices):
    PENDING = "pending", _("Pending Credit Note Generation")
    EXPECTED = "expected", _("Expected Credit Note from Supplier")
    RECEIVED = "received", _("Credit Note Received")
    POSTED = "posted", _("Credit Note Posted to Accounts Payable")
    CANCELLED = "cancelled", _("Cancelled")

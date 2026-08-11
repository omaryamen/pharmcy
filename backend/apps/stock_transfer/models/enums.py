"""Domain choices and text enums for Enterprise Stock Transfer module."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TransferType(models.TextChoices):
    LOCATION_TRANSFER = "location_transfer", _("Storage Location Transfer")
    WAREHOUSE_TRANSFER = "warehouse_transfer", _("Warehouse Transfer")
    BRANCH_TRANSFER = "branch_transfer", _("Inter-Branch Transfer")
    EMERGENCY_TRANSFER = "emergency_transfer", _("Emergency Transfer")
    RETURN_TRANSFER = "return_transfer", _("Return Transfer")
    QUARANTINE_TRANSFER = "quarantine_transfer", _("Quarantine Transfer")
    OTHER = "other", _("Other Transfer")


class TransferPriority(models.TextChoices):
    LOW = "low", _("Low Priority")
    MEDIUM = "medium", _("Medium Priority")
    HIGH = "high", _("High Priority")
    URGENT = "urgent", _("Urgent / Emergency")


class TransferStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    PICKING = "picking", _("Picking In Progress")
    READY_FOR_DISPATCH = "ready_for_dispatch", _("Ready for Dispatch")
    DISPATCHED = "dispatched", _("Dispatched")
    IN_TRANSIT = "in_transit", _("In Transit")
    PARTIALLY_RECEIVED = "partially_received", _("Partially Received")
    RECEIVED = "received", _("Fully Received")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")
    DISCREPANCY = "discrepancy", _("Discrepancy Reported")
    CLOSED = "closed", _("Closed / Completed")


class TransferLineStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PICKED = "picked", _("Picked")
    DISPATCHED = "dispatched", _("Dispatched")
    RECEIVED = "received", _("Received")
    PARTIAL = "partial", _("Partially Received")
    REJECTED = "rejected", _("Rejected")
    DAMAGED = "damaged", _("Damaged")
    DISCREPANCY = "discrepancy", _("Discrepancy Reported")


class DiscrepancyType(models.TextChoices):
    SHORTAGE = "shortage", _("Quantity Shortage")
    OVERAGE = "overage", _("Quantity Overage")
    DAMAGE = "damage", _("Damaged Goods")
    WRONG_BATCH = "wrong_batch", _("Wrong Batch Received")
    WRONG_MEDICINE = "wrong_medicine", _("Wrong Medicine Received")
    WRONG_QUANTITY = "wrong_quantity", _("Wrong Quantity")
    MISSING_ITEM = "missing_item", _("Missing Item")
    OTHER = "other", _("Other Discrepancy")


class DiscrepancyStatus(models.TextChoices):
    REPORTED = "reported", _("Reported")
    UNDER_REVIEW = "under_review", _("Under Review")
    RESOLVED = "resolved", _("Resolved")
    REJECTED = "rejected", _("Rejected")

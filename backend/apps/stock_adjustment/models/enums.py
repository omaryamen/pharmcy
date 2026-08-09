"""Domain choices for Enterprise Stock Adjustment & Stock Count module."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class CountType(models.TextChoices):
    FULL_COUNT = "full_count", _("Full Stock Count")
    PARTIAL_COUNT = "partial_count", _("Partial Stock Count")
    CYCLE_COUNT = "cycle_count", _("Cycle Count")
    SPOT_COUNT = "spot_count", _("Spot Check Count")
    RECOUNT = "recount", _("Recount Session")
    BLIND_COUNT = "blind_count", _("Blind Stock Count")
    BATCH_COUNT = "batch_count", _("Batch-Specific Count")
    LOCATION_COUNT = "location_count", _("Location-Specific Count")
    WAREHOUSE_COUNT = "warehouse_count", _("Warehouse-Wide Count")


class CountStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PLANNED = "planned", _("Planned")
    IN_PROGRESS = "in_progress", _("In Progress")
    SUBMITTED = "submitted", _("Submitted for Review")
    UNDER_REVIEW = "under_review", _("Under Review")
    RECOUNT_REQUIRED = "recount_required", _("Recount Required")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    RECONCILED = "reconciled", _("Reconciled & Adjusted")
    CANCELLED = "cancelled", _("Cancelled")
    REJECTED = "rejected", _("Rejected")


class CountScopeType(models.TextChoices):
    TENANT = "tenant", _("Tenant-Wide")
    COMPANY = "company", _("Company-Wide")
    BRANCH = "branch", _("Branch-Wide")
    WAREHOUSE = "warehouse", _("Warehouse-Wide")
    LOCATION = "location", _("Storage Location")
    MEDICINE = "medicine", _("Medicine Master")
    MEDICINE_CATEGORY = "medicine_category", _("Medicine Category")
    BATCH = "batch", _("Specific Batch")
    CUSTOM_SET = "custom_set", _("Custom Selected Set")


class AdjustmentReason(models.TextChoices):
    COUNT_VARIANCE = "count_variance", _("Physical Count Variance")
    DAMAGE = "damage", _("Damaged Stock")
    EXPIRY = "expiry", _("Expired Stock")
    LOSS = "loss", _("Stock Loss / Theft")
    FOUND_STOCK = "found_stock", _("Surplus Found Stock")
    DATA_CORRECTION = "data_correction", _("Data Entry Correction")
    OPENING_BALANCE_CORRECTION = "opening_balance_correction", _("Opening Balance Correction")
    OTHER = "other", _("Other Reason")


class VarianceDirection(models.TextChoices):
    SHORTAGE = "shortage", _("Shortage (-)")
    OVERAGE = "overage", _("Overage (+)")
    NO_VARIANCE = "no_variance", _("No Variance (Exact Match)")


class SessionStatus(models.TextChoices):
    ACTIVE = "active", _("Active Session")
    COMPLETED = "completed", _("Completed Session")
    CANCELLED = "cancelled", _("Cancelled Session")


class RecountStatus(models.TextChoices):
    REQUESTED = "requested", _("Recount Requested")
    IN_PROGRESS = "in_progress", _("Recount In Progress")
    COMPLETED = "completed", _("Recount Completed")
    APPROVED = "approved", _("Recount Approved")
    REJECTED = "rejected", _("Recount Rejected")

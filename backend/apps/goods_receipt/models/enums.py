"""Domain choices & enums for Enterprise Goods Receipt & Receiving Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReceiptStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    RECEIVING = "receiving", _("Receiving in Progress")
    PENDING_VERIFICATION = "pending_verification", _("Pending Inspection & Verification")
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    PARTIALLY_RECEIVED = "partially_received", _("Partially Received")
    COMPLETED = "completed", _("Completed & Posted")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")


class QualityStatus(models.TextChoices):
    ACCEPTED = "accepted", _("Accepted - Quality Verified")
    REJECTED = "rejected", _("Rejected - Failed Inspection")
    QUARANTINED = "quarantined", _("Quarantined for Inspection")
    DAMAGED = "damaged", _("Damaged Goods")
    PENDING_INSPECTION = "pending_inspection", _("Pending Inspection")
    EXPIRED = "expired", _("Expired Stock")
    RECALLED = "recalled", _("Recalled Batch")


class OverReceivingPolicy(models.TextChoices):
    REJECT = "reject", _("Reject Any Over-Receiving")
    ALLOW_WITHIN_TOLERANCE = "allow_within_tolerance", _("Allow Within Tolerance Percentage")
    REQUIRE_APPROVAL = "require_approval", _("Require Manager Approval")
    ALLOW = "allow", _("Allow Unrestricted Over-Receiving")

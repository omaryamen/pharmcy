"""Domain choices & enums for Enterprise Prescription Management & Pharmacy Dispensing."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class PrescriptionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Prescription")
    PENDING_VERIFICATION = "pending_verification", _("Pending Clinical Verification")
    VERIFIED = "verified", _("Clinically Verified")
    PARTIALLY_DISPENSED = "partially_dispensed", _("Partially Dispensed")
    FULLY_DISPENSED = "fully_dispensed", _("Fully Dispensed")
    CANCELLED = "cancelled", _("Cancelled")
    EXPIRED = "expired", _("Expired")
    REJECTED = "rejected", _("Rejected")


class PrescriptionType(models.TextChoices):
    REGULAR = "regular", _("Regular Prescription")
    CONTROLLED_CLASS_A = "controlled_class_a", _("Controlled Substance Class A")
    CONTROLLED_CLASS_B = "controlled_class_b", _("Controlled Substance Class B")
    NARCOTIC = "narcotic", _("Narcotic / Psychotropic Drug")
    CHRONIC_REFILL = "chronic_refill", _("Chronic Disease Refill")
    EMERGENCY = "emergency", _("Emergency Prescription")


class PrescriptionLineStatus(models.TextChoices):
    PENDING = "pending", _("Pending Dispensing")
    DISPENSED = "dispensed", _("Fully Dispensed")
    PARTIALLY_DISPENSED = "partially_dispensed", _("Partially Dispensed")
    CANCELLED = "cancelled", _("Cancelled")
    SUBSTITUTED = "substituted", _("Substituted")


class DispenseStatus(models.TextChoices):
    COMPLETED = "completed", _("Completed Dispensing")
    CANCELLED = "cancelled", _("Cancelled")
    REVERSED = "reversed", _("Reversed")

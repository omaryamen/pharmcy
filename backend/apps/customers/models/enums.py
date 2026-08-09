"""Domain enumeration choices for Enterprise Customer Management."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomerType(models.TextChoices):
    INDIVIDUAL = "individual", _("Individual")
    ORGANIZATION = "organization", _("Organization")
    CORPORATE = "corporate", _("Corporate")
    INSURANCE = "insurance", _("Insurance Customer")
    WALK_IN = "walk_in", _("Walk-in Customer")
    ANONYMOUS = "anonymous", _("Anonymous Customer")


class CustomerStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    BLOCKED = "blocked", _("Blocked")
    SUSPENDED = "suspended", _("Suspended")
    ARCHIVED = "archived", _("Archived")


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")
    UNSPECIFIED = "unspecified", _("Unspecified")


class CreditStatus(models.TextChoices):
    NORMAL = "normal", _("Normal")
    WARNING = "warning", _("Warning")
    BLOCKED = "blocked", _("Blocked")
    SUSPENDED = "suspended", _("Suspended")


class InsuranceCoverageStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    EXPIRED = "expired", _("Expired")
    PENDING = "pending", _("Pending")
    NONE = "none", _("None")


class AddressType(models.TextChoices):
    HOME = "home", _("Home")
    WORK = "work", _("Work")
    BILLING = "billing", _("Billing")
    DELIVERY = "delivery", _("Delivery")
    OTHER = "other", _("Other")


class BloodType(models.TextChoices):
    A_POSITIVE = "A+", "A+"
    A_NEGATIVE = "A-", "A-"
    B_POSITIVE = "B+", "B+"
    B_NEGATIVE = "B-", "B-"
    AB_POSITIVE = "AB+", "AB+"
    AB_NEGATIVE = "AB-", "AB-"
    O_POSITIVE = "O+", "O+"
    O_NEGATIVE = "O-", "O-"
    UNKNOWN = "unknown", _("Unknown")

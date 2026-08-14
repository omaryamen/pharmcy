"""Domain choices & enums for Enterprise SaaS Subscription, Billing & Licensing Platform."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SaaSBillingCycle(models.TextChoices):
    MONTHLY = "monthly", _("Monthly")
    QUARTERLY = "quarterly", _("Quarterly")
    SEMI_ANNUAL = "semi_annual", _("Semi-Annual")
    ANNUAL = "annual", _("Annual")


class SaaSSubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    PAST_DUE = "past_due", _("Past Due")
    GRACE_PERIOD = "grace_period", _("Grace Period")
    SUSPENDED = "suspended", _("Suspended")
    CANCELLED = "cancelled", _("Cancelled")
    EXPIRED = "expired", _("Expired")
    INCOMPLETE = "incomplete", _("Incomplete")
    PENDING = "pending", _("Pending Activation")


class SaaSInvoiceStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    OPEN = "open", _("Open / Issued")
    PAID = "paid", _("Paid")
    PARTIALLY_PAID = "partially_paid", _("Partially Paid")
    PAST_DUE = "past_due", _("Past Due")
    VOID = "void", _("Void")
    UNCOLLECTIBLE = "uncollectible", _("Uncollectible")
    REFUNDED = "refunded", _("Refunded")


class SaaSLineItemType(models.TextChoices):
    PLAN_FEE = "plan_fee", _("Subscription Plan Fee")
    ADD_ON = "add_on", _("Add-On Fee")
    OVERAGE = "overage", _("Usage Overage Charge")
    PRORATION_CREDIT = "proration_credit", _("Proration Credit Adjustment")
    DISCOUNT = "discount", _("Discount")
    TAX = "tax", _("Tax Charge")
    ONE_TIME = "one_time", _("One-Time Charge")


class SaaSPaymentStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PROCESSING = "processing", _("Processing")
    SUCCEEDED = "succeeded", _("Succeeded")
    FAILED = "failed", _("Failed")
    CANCELLED = "cancelled", _("Cancelled")
    REFUNDED = "refunded", _("Refunded")
    PARTIALLY_REFUNDED = "partially_refunded", _("Partially Refunded")


class SaaSLicenseType(models.TextChoices):
    SUBSCRIPTION = "subscription", _("Subscription License")
    TRIAL = "trial", _("Trial License")
    ENTERPRISE = "enterprise", _("Enterprise On-Prem/Hybrid License")
    EVALUATION = "evaluation", _("Evaluation License")


class SaaSLicenseStatus(models.TextChoices):
    ACTIVE = "active", _("Active License")
    TRIAL = "trial", _("Trial License")
    SUSPENDED = "suspended", _("Suspended")
    EXPIRED = "expired", _("Expired")
    REVOKED = "revoked", _("Revoked")


class CouponDiscountType(models.TextChoices):
    PERCENTAGE = "percentage", _("Percentage Discount")
    FIXED_AMOUNT = "fixed_amount", _("Fixed Amount Discount")

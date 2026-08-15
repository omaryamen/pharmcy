"""Domain choices & enums for Enterprise Pharma E-Commerce & B2B Marketplace."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class StoreStatus(models.TextChoices):
    ACTIVE = "active", _("Active Storefront")
    MAINTENANCE = "maintenance", _("Storefront Under Maintenance")
    DISABLED = "disabled", _("Disabled")


class CommerceOrderStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Order")
    PENDING = "pending", _("Pending Order")
    CONFIRMED = "confirmed", _("Confirmed")
    PAYMENT_PENDING = "payment_pending", _("Payment Pending")
    PAID = "paid", _("Paid")
    PROCESSING = "processing", _("Processing / Picking")
    READY_FOR_PICKUP = "ready_for_pickup", _("Ready For Pickup")
    OUT_FOR_DELIVERY = "out_for_delivery", _("Out For Delivery")
    DELIVERED = "delivered", _("Delivered")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    REFUNDED = "refunded", _("Refunded")


class CommercePaymentStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PAID = "paid", _("Paid Successfully")
    FAILED = "failed", _("Payment Failed")
    REFUNDED = "refunded", _("Refunded")
    PARTIALLY_REFUNDED = "partially_refunded", _("Partially Refunded")


class DeliveryMethod(models.TextChoices):
    PICKUP = "pickup", _("Branch / Store Pickup")
    STANDARD_DELIVERY = "standard", _("Standard Delivery")
    EXPRESS_DELIVERY = "express", _("Express Courier Delivery")


class PrescriptionReviewStatus(models.TextChoices):
    UPLOADED = "uploaded", _("Uploaded - Awaiting Review")
    UNDER_REVIEW = "under_review", _("Under Pharmacist Review")
    APPROVED = "approved", _("Approved by Pharmacist")
    REJECTED = "rejected", _("Rejected")
    EXPIRED = "expired", _("Expired")


class CouponDiscountType(models.TextChoices):
    PERCENTAGE = "percentage", _("Percentage Discount")
    FIXED_AMOUNT = "fixed_amount", _("Fixed Amount Discount")

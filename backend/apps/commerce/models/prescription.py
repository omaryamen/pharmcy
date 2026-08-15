"""OrderPrescription model for digital prescription upload and pharmacist verification."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.enums import PrescriptionReviewStatus
from apps.commerce.models.order import CommerceOrder


class OrderPrescription(TenantAwareModel, FullAuditModel):
    """Prescription document uploaded by customer for online orders containing Rx medicines."""

    order = models.ForeignKey(
        CommerceOrder,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        verbose_name=_("Commerce Order"),
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="uploaded_prescriptions",
        verbose_name=_("Customer"),
    )

    file_url = models.URLField(max_length=500, verbose_name=_("Secure Storage File URL"))
    file_type = models.CharField(max_length=20, default="image/jpeg", verbose_name=_("MIME Content Type"))

    review_status = models.CharField(
        max_length=30,
        choices=PrescriptionReviewStatus.choices,
        default=PrescriptionReviewStatus.UPLOADED,
        db_index=True,
        verbose_name=_("Pharmacist Review Status"),
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_order_prescriptions",
        null=True,
        blank=True,
        verbose_name=_("Reviewing Pharmacist"),
    )

    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reviewed Timestamp"))
    pharmacist_notes = models.TextField(blank=True, default="", verbose_name=_("Pharmacist Clinical Notes"))

    class Meta:
        db_table = "commerce_order_prescriptions"
        verbose_name = _("Order Prescription")
        verbose_name_plural = _("Order Prescriptions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Rx for Order {self.order.order_number} [{self.review_status}]"

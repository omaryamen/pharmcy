"""OrderDelivery model managing delivery dispatch, courier references, and tracking numbers."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.order import CommerceOrder


class OrderDelivery(TenantAwareModel, FullAuditModel):
    """Digital delivery shipment tracking for a fulfilled commerce order."""

    order = models.OneToOneField(
        CommerceOrder,
        on_delete=models.CASCADE,
        related_name="delivery_record",
        verbose_name=_("Commerce Order"),
    )

    tracking_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Courier Tracking Number"))
    courier_name = models.CharField(max_length=100, verbose_name=_("Courier Provider Name"))

    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name=_("Estimated Delivery Timestamp"))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Delivered Timestamp"))

    delivery_notes = models.TextField(blank=True, default="", verbose_name=_("Delivery Instructions / Notes"))

    class Meta:
        db_table = "commerce_order_deliveries"
        verbose_name = _("Order Delivery")
        verbose_name_plural = _("Order Deliveries")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Delivery {self.tracking_number} ({self.courier_name}) for Order {self.order.order_number}"

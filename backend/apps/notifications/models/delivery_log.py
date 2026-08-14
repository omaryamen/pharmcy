"""NotificationDelivery model for auditing multi-channel dispatch attempts."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import NotificationChannel, NotificationStatus
from apps.notifications.models.notification import Notification


class NotificationDelivery(TenantAwareModel, FullAuditModel):
    """Audit record capturing single dispatch attempts and provider status responses."""

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="delivery_attempts",
        verbose_name=_("Notification"),
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        verbose_name=_("Channel"),
    )
    provider_name = models.CharField(max_length=60, verbose_name=_("Provider Adapter Name"))
    attempt_number = models.IntegerField(default=1, verbose_name=_("Attempt Number"))

    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name=_("Attempt Status"),
    )

    external_id = models.CharField(max_length=150, blank=True, default="", verbose_name=_("External Provider Reference ID"))
    error_message = models.TextField(blank=True, default="", verbose_name=_("Error Details"))

    class Meta:
        db_table = "notification_delivery_logs"
        verbose_name = _("Notification Delivery Log")
        verbose_name_plural = _("Notification Delivery Logs")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification.notification_number} Attempt #{self.attempt_number} ({self.channel}) [{self.status}]"

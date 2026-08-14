"""Notification model for user-facing alert delivery across all channels."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)
from apps.notifications.models.event import DomainEvent


class Notification(TenantAwareModel, FullAuditModel):
    """Notification entity representing a targeted message generated for a recipient."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Company"),
        null=True,
        blank=True,
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )

    notification_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Notification Number (NOT)"))
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications",
        verbose_name=_("Recipient User"),
        db_index=True,
    )

    title = models.CharField(max_length=200, verbose_name=_("Notification Title"))
    message = models.TextField(verbose_name=_("Notification Message"))

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
        db_index=True,
        verbose_name=_("Delivery Channel"),
    )

    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        db_index=True,
        verbose_name=_("Notification Priority"),
    )

    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
        verbose_name=_("Delivery Status"),
    )

    source_event = models.ForeignKey(
        DomainEvent,
        on_delete=models.SET_NULL,
        related_name="generated_notifications",
        null=True,
        blank=True,
        verbose_name=_("Source Event"),
    )

    action_url = models.CharField(max_length=500, blank=True, default="", verbose_name=_("Action URL"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadata Payload"))

    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Read Timestamp"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expiry Timestamp"))

    class Meta:
        db_table = "notification_records"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification_number} -> {self.recipient} [{self.status}]"

    def mark_as_read(self) -> None:
        """Mark notification as READ by recipient."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = NotificationStatus.READ
            self.save(update_fields=["read_at", "status", "updated_at"])

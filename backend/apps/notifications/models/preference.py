"""NotificationPreference model governing user alert channels, quiet hours, and priority thresholds."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import (
    DigestFrequency,
    EventTypeChoices,
    NotificationChannel,
    NotificationPriority,
)


class NotificationPreference(TenantAwareModel, FullAuditModel):
    """User-specific alert preference settings governing channel opt-ins and quiet hours."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("User"),
        db_index=True,
    )

    event_type = models.CharField(
        max_length=100,
        choices=EventTypeChoices.choices,
        db_index=True,
        verbose_name=_("Event Type"),
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
        verbose_name=_("Channel"),
    )

    is_enabled = models.BooleanField(default=True, verbose_name=_("Is Channel Enabled"))

    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name=_("Quiet Hours Start Time"))
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name=_("Quiet Hours End Time"))

    minimum_priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name=_("Minimum Priority Threshold"),
    )

    digest_frequency = models.CharField(
        max_length=20,
        choices=DigestFrequency.choices,
        default=DigestFrequency.IMMEDIATE,
        verbose_name=_("Digest Frequency"),
    )

    class Meta:
        db_table = "notification_user_preferences"
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user", "event_type", "channel"],
                name="pref_user_event_channel_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.event_type} ({self.channel}): Enabled={self.is_enabled}"

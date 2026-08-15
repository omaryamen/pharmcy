"""Device and DeviceSession models tracking mobile devices and push tokens."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.mobile_api.models.enums import DevicePlatform


class Device(TenantAwareModel, FullAuditModel):
    """Mobile device registration holding push notification tokens and OS metadata."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mobile_devices",
        verbose_name=_("User Account"),
    )

    device_identifier = models.CharField(max_length=120, db_index=True, verbose_name=_("Hardware / Installation UUID"))
    platform = models.CharField(
        max_length=20,
        choices=DevicePlatform.choices,
        default=DevicePlatform.ANDROID,
        verbose_name=_("Device Platform"),
    )

    app_version = models.CharField(max_length=30, blank=True, default="1.0.0", verbose_name=_("Mobile App Version"))
    os_version = models.CharField(max_length=30, blank=True, default="", verbose_name=_("Operating System Version"))
    push_token = models.TextField(blank=True, default="", verbose_name=_("FCM / APNs Push Token"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Device Active"))
    last_seen = models.DateTimeField(default=timezone.now, verbose_name=_("Last Seen Timestamp"))

    class Meta:
        db_table = "mobile_devices"
        verbose_name = _("Mobile Device")
        verbose_name_plural = _("Mobile Devices")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "device_identifier"],
                name="mobile_user_device_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.platform} ({self.device_identifier}) [Active={self.is_active}]"

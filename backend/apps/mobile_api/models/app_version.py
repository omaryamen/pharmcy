"""MobileAppVersion model managing client upgrade policies and force update prompts."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.mobile_api.models.enums import DevicePlatform


class MobileAppVersion(FullAuditModel):
    """Platform-wide mobile app version control managing minimum supported and recommended releases."""

    platform = models.CharField(
        max_length=20,
        choices=DevicePlatform.choices,
        unique=True,
        verbose_name=_("Client Platform"),
    )

    min_version = models.CharField(max_length=20, default="1.0.0", verbose_name=_("Minimum Supported Version"))
    recommended_version = models.CharField(max_length=20, default="1.0.0", verbose_name=_("Recommended Version"))

    is_force_update = models.BooleanField(default=False, verbose_name=_("Force App Update"))
    maintenance_mode = models.BooleanField(default=False, verbose_name=_("Is Mobile Backend in Maintenance"))
    maintenance_message = models.TextField(blank=True, default="", verbose_name=_("Maintenance Notification Message"))

    class Meta:
        db_table = "mobile_app_versions"
        verbose_name = _("Mobile App Version Policy")
        verbose_name_plural = _("Mobile App Version Policies")

    def __str__(self) -> str:
        return f"{self.platform}: Min={self.min_version}, Rec={self.recommended_version} (Force={self.is_force_update})"

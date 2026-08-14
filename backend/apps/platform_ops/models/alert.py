"""PlatformAlert model capturing infrastructure outages, critical errors, and security alerts for super admins."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.platform_ops.models.enums import AlertCategory, AlertSeverity


class PlatformAlert(FullAuditModel):
    """Platform-level alert raised for infrastructure anomalies, security events, or subscription failures."""

    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.WARNING,
        db_index=True,
        verbose_name=_("Alert Severity"),
    )

    category = models.CharField(
        max_length=30,
        choices=AlertCategory.choices,
        default=AlertCategory.INFRASTRUCTURE,
        db_index=True,
        verbose_name=_("Alert Category"),
    )

    title = models.CharField(max_length=200, verbose_name=_("Alert Title"))
    message = models.TextField(verbose_name=_("Alert Message"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Diagnostic Metadata"))

    is_resolved = models.BooleanField(default=False, db_index=True, verbose_name=_("Is Resolved"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved Timestamp"))
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_platform_alerts",
        null=True,
        blank=True,
        verbose_name=_("Resolved By Admin"),
    )

    class Meta:
        db_table = "platform_alerts"
        verbose_name = _("Platform Alert")
        verbose_name_plural = _("Platform Alerts")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.title} (Resolved={self.is_resolved})"

    def resolve(self, admin_user: Any) -> None:
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = admin_user
        self.save(update_fields=["is_resolved", "resolved_at", "resolved_by", "updated_at"])

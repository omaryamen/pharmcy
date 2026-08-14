"""PlatformAuditLog model recording cross-tenant super-admin administrative actions."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class PlatformAuditLog(FullAuditModel):
    """Global cross-tenant audit log tracking privileged operations (tenant suspension, quota changes, plan upgrades)."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="platform_audit_actions",
        null=True,
        blank=True,
        verbose_name=_("Admin Actor"),
    )

    action = models.CharField(max_length=100, db_index=True, verbose_name=_("Action Code"))
    target_tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.SET_NULL,
        related_name="platform_audits",
        null=True,
        blank=True,
        verbose_name=_("Target Tenant"),
    )

    target_object_type = models.CharField(max_length=60, blank=True, default="", verbose_name=_("Target Object Type"))
    target_object_id = models.CharField(max_length=60, blank=True, default="", verbose_name=_("Target Object ID"))

    description = models.TextField(verbose_name=_("Action Description"))
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Change Delta Payload"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))

    timestamp = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_("Timestamp"))

    class Meta:
        db_table = "platform_audit_logs"
        verbose_name = _("Platform Audit Log")
        verbose_name_plural = _("Platform Audit Logs")
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor} on {self.target_tenant} at {self.timestamp}"

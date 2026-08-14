"""TenantImpersonationLog model auditing Super Admin session impersonation of customer tenants."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class TenantImpersonationLog(FullAuditModel):
    """Audit record capturing every tenant session impersonation initiated by super administrators."""

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="impersonation_sessions",
        verbose_name=_("Super Admin User"),
    )

    impersonated_tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="impersonated_logs",
        verbose_name=_("Impersonated Tenant"),
    )

    reason = models.TextField(verbose_name=_("Impersonation Justification Reason"))
    ticket_reference = models.CharField(max_length=60, blank=True, default="", verbose_name=_("Support Ticket ID"))

    started_at = models.DateTimeField(default=timezone.now, verbose_name=_("Session Started At"))
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Session Ended At"))

    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Client IP Address"))
    actions_count = models.IntegerField(default=0, verbose_name=_("Actions Performed Count"))

    class Meta:
        db_table = "platform_impersonation_logs"
        verbose_name = _("Tenant Impersonation Log")
        verbose_name_plural = _("Tenant Impersonation Logs")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.admin_user} impersonated {self.impersonated_tenant.name} at {self.started_at}"

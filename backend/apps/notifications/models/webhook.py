"""WebhookEndpoint model managing outbound webhook registrations and security secrets."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class WebhookEndpoint(TenantAwareModel, FullAuditModel):
    """Outbound webhook registration for broadcasting real-time ERP events to external integrations."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
        null=True,
        blank=True,
        verbose_name=_("Company"),
        db_index=True,
    )

    name = models.CharField(max_length=150, verbose_name=_("Webhook Name"))
    target_url = models.URLField(max_length=500, verbose_name=_("Target HTTP URL"))
    secret = models.CharField(max_length=128, verbose_name=_("HMAC Signing Secret"))

    subscribed_events = models.JSONField(default=list, verbose_name=_("Subscribed Event Types"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    last_delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Successful Delivery"))

    class Meta:
        db_table = "notification_webhooks"
        verbose_name = _("Webhook Endpoint")
        verbose_name_plural = _("Webhook Endpoints")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.target_url}) [Active={self.is_active}]"

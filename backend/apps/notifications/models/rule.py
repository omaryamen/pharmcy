"""NotificationRule model governing event routing, conditions, roles, and escalation."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import EventTypeChoices, NotificationChannel, NotificationPriority
from apps.notifications.models.template import NotificationTemplate


class NotificationRule(TenantAwareModel, FullAuditModel):
    """Rule engine definition mapping events and conditions to target roles and templates."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="notification_rules",
        null=True,
        blank=True,
        verbose_name=_("Company"),
        db_index=True,
    )

    code = models.CharField(max_length=60, db_index=True, verbose_name=_("Rule Code"))
    name = models.CharField(max_length=150, verbose_name=_("Rule Name"))

    event_type = models.CharField(
        max_length=100,
        choices=EventTypeChoices.choices,
        db_index=True,
        verbose_name=_("Triggering Event Type"),
    )

    condition_json = models.JSONField(default=dict, blank=True, verbose_name=_("Condition Expression JSON"))

    target_role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.SET_NULL,
        related_name="notification_rules",
        null=True,
        blank=True,
        verbose_name=_("Target RBAC Role"),
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
        verbose_name=_("Channel"),
    )

    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        related_name="notification_rules",
        null=True,
        blank=True,
        verbose_name=_("Notification Template"),
    )

    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name=_("Priority"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active Rule"))
    cooldown_minutes = models.IntegerField(default=15, verbose_name=_("Alert Deduplication Cooldown Minutes"))

    class Meta:
        db_table = "notification_rules"
        verbose_name = _("Notification Rule")
        verbose_name_plural = _("Notification Rules")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="rule_tenant_code_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name} [{self.event_type}]"

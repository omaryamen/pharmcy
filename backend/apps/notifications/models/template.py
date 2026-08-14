"""NotificationTemplate model for rendering localized multi-channel messages."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import EventTypeChoices, NotificationChannel


class NotificationTemplate(TenantAwareModel, FullAuditModel):
    """Template model defining localized subjects and body formats with safe variable placeholders."""

    code = models.CharField(max_length=60, db_index=True, verbose_name=_("Template Code"))
    name = models.CharField(max_length=150, verbose_name=_("Template Name"))

    event_type = models.CharField(
        max_length=100,
        choices=EventTypeChoices.choices,
        db_index=True,
        verbose_name=_("Target Event Type"),
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
        verbose_name=_("Delivery Channel"),
    )

    language = models.CharField(max_length=10, default="en", verbose_name=_("Language Code (e.g. 'en', 'ar')"))

    subject_template = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Subject Template"))
    body_template = models.TextField(verbose_name=_("Body Template Text"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "notification_templates"
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code", "language"],
                name="tmpl_tenant_code_lang_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.language}) [{self.channel}]"

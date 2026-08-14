"""DeadLetterEvent model storing permanently failed events for administrative review."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.event import DomainEvent


class DeadLetterEvent(TenantAwareModel, FullAuditModel):
    """Dead letter repository capturing permanently unprocessable events."""

    dead_letter_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Dead Letter Number (DLE)"))
    event = models.ForeignKey(
        DomainEvent,
        on_delete=models.CASCADE,
        related_name="dead_letter_records",
        verbose_name=_("Domain Event"),
    )

    failure_reason = models.TextField(verbose_name=_("Failure Reason / Traceback"))
    retry_count = models.IntegerField(default=0, verbose_name=_("Total Retries Attempted"))

    is_resolved = models.BooleanField(default=False, verbose_name=_("Is Resolved"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_dead_letters",
        null=True,
        blank=True,
        verbose_name=_("Resolved By User"),
    )

    class Meta:
        db_table = "notification_dead_letters"
        verbose_name = _("Dead Letter Event")
        verbose_name_plural = _("Dead Letter Events")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.dead_letter_number} - Event {self.event.event_number} [Resolved={self.is_resolved}]"

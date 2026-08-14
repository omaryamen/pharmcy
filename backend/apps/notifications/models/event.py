"""DomainEvent and OutboxEvent models for event-driven architecture and transaction outbox pattern."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.notifications.models.enums import EventStatus, EventTypeChoices


class DomainEvent(TenantAwareModel, FullAuditModel):
    """Authoritative Domain Event record capturing state changes across all ERP modules."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="domain_events",
        verbose_name=_("Company"),
        null=True,
        blank=True,
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="domain_events",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )

    event_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Event Number (EVT)"))
    event_type = models.CharField(
        max_length=100,
        choices=EventTypeChoices.choices,
        db_index=True,
        verbose_name=_("Event Type"),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="triggered_events",
        null=True,
        blank=True,
        verbose_name=_("Actor User"),
    )

    source_module = models.CharField(max_length=60, db_index=True, verbose_name=_("Source ERP Module"))
    source_object_id = models.CharField(max_length=100, db_index=True, verbose_name=_("Source Object ID"))

    payload = models.JSONField(default=dict, verbose_name=_("Event Data Payload"))
    occurred_at = models.DateTimeField(default=timezone.now, verbose_name=_("Occurred Timestamp"))

    correlation_id = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Correlation ID"))
    causation_id = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Causation ID"))
    idempotency_key = models.CharField(max_length=120, db_index=True, verbose_name=_("Idempotency Key"))

    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.PENDING,
        db_index=True,
        verbose_name=_("Event Processing Status"),
    )
    retry_count = models.IntegerField(default=0, verbose_name=_("Retry Count"))
    last_error = models.TextField(blank=True, default="", verbose_name=_("Last Error Message"))

    class Meta:
        db_table = "notification_domain_events"
        verbose_name = _("Domain Event")
        verbose_name_plural = _("Domain Events")
        ordering = ["-occurred_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                name="evt_tenant_idempotency_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.event_number} - {self.event_type} [{self.status}]"


class OutboxEvent(TenantAwareModel, FullAuditModel):
    """Outbox Pattern record for transaction-safe event queueing without lost events."""

    domain_event = models.OneToOneField(
        DomainEvent,
        on_delete=models.CASCADE,
        related_name="outbox_record",
        verbose_name=_("Domain Event"),
    )

    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.PENDING,
        db_index=True,
        verbose_name=_("Outbox Status"),
    )
    scheduled_at = models.DateTimeField(default=timezone.now, verbose_name=_("Scheduled Processing Time"))
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))

    class Meta:
        db_table = "notification_outbox_events"
        verbose_name = _("Outbox Event")
        verbose_name_plural = _("Outbox Events")
        ordering = ["scheduled_at"]

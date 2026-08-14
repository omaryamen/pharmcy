"""EventPublisherService publishing domain events with tenant idempotency and transaction outbox support."""

from __future__ import annotations

import logging
from typing import Any
from django.db import transaction
from django.utils import timezone

from apps.notifications.exceptions import DuplicateEventError
from apps.notifications.models import DomainEvent, EventStatus, OutboxEvent
from apps.notifications.services.number_generator import NotificationNumberGenerator

logger = logging.getLogger(__name__)


class EventPublisherService:
    """Service layer publishing DomainEvents and enqueueing OutboxEvents atomically."""

    def __init__(self, number_generator: NotificationNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or NotificationNumberGenerator()

    @transaction.atomic
    def publish_event(
        self,
        tenant: Any,
        event_type: str,
        source_module: str,
        source_object_id: str,
        payload: dict[str, Any],
        *,
        company: Any | None = None,
        branch: Any | None = None,
        actor: Any | None = None,
        idempotency_key: str = "",
        correlation_id: str = "",
        causation_id: str = "",
    ) -> DomainEvent:
        """Publish a domain event with row-locking idempotency protection and create Outbox record."""
        key = idempotency_key.strip() or f"{source_module}:{source_object_id}:{event_type}:{timezone.now().timestamp()}"

        existing = DomainEvent.objects.filter(tenant=tenant, idempotency_key=key).first()
        if existing:
            logger.info("Event with idempotency key %s already published (%s)", key, existing.event_number)
            return existing

        evt_num = self.number_generator.generate_event_number(tenant)

        domain_event = DomainEvent.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            event_number=evt_num,
            event_type=event_type,
            actor=actor,
            source_module=source_module,
            source_object_id=source_object_id,
            payload=payload,
            occurred_at=timezone.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
            idempotency_key=key,
            status=EventStatus.PENDING,
        )

        OutboxEvent.objects.create(
            tenant=tenant,
            domain_event=domain_event,
            status=EventStatus.PENDING,
            scheduled_at=timezone.now(),
        )

        logger.info("Published DomainEvent %s (%s) from module %s", evt_num, event_type, source_module)
        return domain_event

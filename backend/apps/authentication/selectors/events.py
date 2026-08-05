"""Security event read queries."""

from __future__ import annotations

from django.db.models import QuerySet

from ..models import SecurityEvent, SecurityEventType


def event_queryset_for_user(user, *, event_type: SecurityEventType | str | None = None) -> QuerySet[SecurityEvent]:
    """Security events for ``user``, most recent first, optionally filtered."""
    queryset = SecurityEvent.objects.filter(user=user)
    if event_type is not None:
        queryset = queryset.filter(event_type=event_type)
    return queryset.order_by("-created_at")


def recent_events_for_user(user, *, limit: int = 20) -> QuerySet[SecurityEvent]:
    return event_queryset_for_user(user)[:limit]

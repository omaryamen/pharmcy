"""Sequence generator for notifications, events, and dead letter records."""

import uuid
from typing import Any
from django.utils import timezone


class NotificationNumberGenerator:
    """Collision-safe sequence number generator for events and notifications."""

    def generate_event_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"EVT-{year}-{uid}"

    def generate_notification_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"NOT-{year}-{uid}"

    def generate_dead_letter_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"DLE-{year}-{uid}"

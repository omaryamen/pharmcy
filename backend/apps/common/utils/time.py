"""Time helpers. All datetimes are stored in UTC (USE_TZ=True)."""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone


def now_utc() -> datetime:
    return timezone.now()


def utc_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
    return value.isoformat()

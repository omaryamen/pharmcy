"""Security event persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.common.repositories.base import BaseRepository

from ..models import SecurityEvent, SecurityEventType


class SecurityEventRepository(BaseRepository[SecurityEvent]):
    model = SecurityEvent

    def for_user(self, user) -> QuerySet[SecurityEvent]:
        return self.filter(user=user)

    def record(
        self,
        *,
        user,
        event_type: SecurityEventType,
        request=None,
        session=None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_name: str = "",
    ) -> SecurityEvent:
        return SecurityEvent.record(
            user=user,
            event_type=event_type,
            request=request,
            session=session,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
        )

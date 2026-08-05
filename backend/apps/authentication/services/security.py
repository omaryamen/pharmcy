"""Security event service: read access to the audit trail."""

from __future__ import annotations

from apps.core.models import User

from ..models import SecurityEventType
from ..repositories import SecurityEventRepository
from ..selectors import event_queryset_for_user


class SecurityEventService:
    """Query the authenticated user's security audit trail."""

    def __init__(self, event_repository: SecurityEventRepository | None = None) -> None:
        self.events = event_repository or SecurityEventRepository()

    def list_events(
        self,
        *,
        user: User,
        event_type: SecurityEventType | str | None = None,
        limit: int = 100,
    ):
        return event_queryset_for_user(user, event_type=event_type)[:limit]

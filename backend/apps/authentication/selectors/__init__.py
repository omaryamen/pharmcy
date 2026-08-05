"""Authentication selectors.

Read-side queries that keep aggregation / listing logic out of services and
views. Services still enforce policy; selectors only shape reads.
"""

from .events import event_queryset_for_user, recent_events_for_user
from .sessions import active_session_count, sessions_for_user

__all__ = [
    "active_session_count",
    "event_queryset_for_user",
    "recent_events_for_user",
    "sessions_for_user",
]

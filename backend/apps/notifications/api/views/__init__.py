"""Export views for apps.notifications."""

from apps.notifications.api.views.notification_views import NotificationViewSet
from apps.notifications.api.views.preference_views import NotificationPreferenceViewSet

__all__ = [
    "NotificationViewSet",
    "NotificationPreferenceViewSet",
]

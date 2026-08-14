"""Export serializers for apps.notifications."""

from apps.notifications.api.serializers.notification import NotificationSerializer
from apps.notifications.api.serializers.preference import NotificationPreferenceSerializer

__all__ = [
    "NotificationSerializer",
    "NotificationPreferenceSerializer",
]

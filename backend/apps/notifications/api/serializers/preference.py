"""DRF Serializer for NotificationPreference model."""

from rest_framework import serializers
from apps.notifications.models import NotificationPreference


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "event_type",
            "channel",
            "is_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "minimum_priority",
            "digest_frequency",
        ]
        read_only_fields = ["id"]

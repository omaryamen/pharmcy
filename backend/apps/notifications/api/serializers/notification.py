"""DRF Serializer for Notification model."""

from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_number",
            "title",
            "message",
            "channel",
            "priority",
            "status",
            "action_url",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "notification_number", "created_at"]

"""DRF Serializer for PlatformAlert."""

from rest_framework import serializers
from apps.platform_ops.models import PlatformAlert


class PlatformAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformAlert
        fields = [
            "id",
            "severity",
            "category",
            "title",
            "message",
            "metadata",
            "is_resolved",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "resolved_at", "created_at"]

"""DRF Serializer for MobileSyncQueue."""

from rest_framework import serializers
from apps.mobile_api.models import MobileSyncQueue


class MobileSyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileSyncQueue
        fields = [
            "id",
            "entity_type",
            "client_mutation_id",
            "operation",
            "payload",
            "client_version",
            "status",
            "conflict_reason",
            "synced_at",
        ]
        read_only_fields = ["id", "status", "conflict_reason", "synced_at"]

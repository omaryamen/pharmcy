"""DRF Serializer for SystemMaintenanceWindow."""

from rest_framework import serializers
from apps.platform_ops.models import SystemMaintenanceWindow


class SystemMaintenanceWindowSerializer(serializers.ModelSerializer):
    is_in_effect = serializers.BooleanField(source="is_currently_in_effect", read_only=True)

    class Meta:
        model = SystemMaintenanceWindow
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "is_active",
            "is_in_effect",
            "bypass_key",
            "affected_services",
        ]
        read_only_fields = ["id", "bypass_key"]

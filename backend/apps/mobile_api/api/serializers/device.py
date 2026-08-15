"""DRF Serializer for Device."""

from rest_framework import serializers
from apps.mobile_api.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id",
            "device_identifier",
            "platform",
            "app_version",
            "os_version",
            "push_token",
            "is_active",
            "last_seen",
        ]
        read_only_fields = ["id", "last_seen"]

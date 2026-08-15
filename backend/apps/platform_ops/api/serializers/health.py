"""DRF Serializer for SystemHealthCheck."""

from rest_framework import serializers
from apps.platform_ops.models import SystemHealthCheck


class SystemHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthCheck
        fields = ["id", "component_name", "status", "latency_ms", "checked_at", "details", "error_message"]
        read_only_fields = ["id", "checked_at"]

"""Security event serializer."""

from __future__ import annotations

from rest_framework import serializers

from ..models import SecurityEvent


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ("id", "event_type", "ip_address", "device_name", "details", "created_at")
        read_only_fields = fields

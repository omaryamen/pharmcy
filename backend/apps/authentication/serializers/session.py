"""Login session serializer."""

from __future__ import annotations

from rest_framework import serializers

from ..models import LoginSession


class LoginSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginSession
        fields = (
            "id",
            "device_name",
            "device_type",
            "ip_address",
            "remember_me",
            "is_active",
            "is_expired",
            "created_at",
            "last_used_at",
            "expires_at",
            "revoked_at",
            "revoked_reason",
        )
        read_only_fields = fields

    is_expired = serializers.ReadOnlyField(source="is_expired")

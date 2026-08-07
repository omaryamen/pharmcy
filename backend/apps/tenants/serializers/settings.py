"""Tenant Settings serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.tenants.models import TenantSettings


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = [
            "general_settings",
            "localization",
            "tax_configuration",
            "business_hours",
            "feature_flags",
            "password_policy",
            "security_settings",
            "notification_settings",
            "theme",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

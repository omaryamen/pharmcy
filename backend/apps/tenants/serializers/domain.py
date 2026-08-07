"""Tenant Domain serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.tenants.models import TenantDomain
from apps.tenants.validators import validate_domain_name


class TenantDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantDomain
        fields = [
            "id",
            "domain_name",
            "domain_type",
            "is_verified",
            "ssl_status",
            "verification_token",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_verified", "ssl_status", "verification_token", "created_at", "updated_at"]

    def validate_domain_name(self, value: str) -> str:
        return validate_domain_name(value)

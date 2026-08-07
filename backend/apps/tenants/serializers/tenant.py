"""Tenant serializers for lifecycle, creation, management, and details."""

from __future__ import annotations

from rest_framework import serializers

from apps.core.models import Tenant
from apps.tenants.serializers.domain import TenantDomainSerializer
from apps.tenants.serializers.profile import TenantProfileSerializer
from apps.tenants.serializers.settings import TenantSettingsSerializer
from apps.tenants.serializers.subscription import TenantSubscriptionSerializer
from apps.tenants.validators import validate_slug


class TenantSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "code",
            "slug",
            "owner",
            "owner_email",
            "status",
            "timezone",
            "locale",
            "subscription_tier",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "is_deleted", "created_at", "updated_at"]

    def validate_slug(self, value: str) -> str:
        return validate_slug(value)


class TenantCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    slug = serializers.CharField(max_length=100, required=False)
    code = serializers.CharField(max_length=50, required=False)
    legal_name = serializers.CharField(max_length=200, required=False)
    admin_email = serializers.EmailField(required=False)
    admin_password = serializers.CharField(write_only=True, required=False)
    admin_first_name = serializers.CharField(required=False, default="Admin")
    admin_last_name = serializers.CharField(required=False, default="User")
    plan = serializers.CharField(required=False, default="trial")
    billing_cycle = serializers.CharField(required=False, default="monthly")
    country = serializers.CharField(required=False, default="Yemen")
    currency = serializers.CharField(required=False, default="YER")
    custom_domain = serializers.CharField(required=False, allow_blank=True)


class TenantDetailSerializer(TenantSerializer):
    profile = TenantProfileSerializer(read_only=True)
    settings = TenantSettingsSerializer(read_only=True)
    subscription = TenantSubscriptionSerializer(read_only=True)
    domains = TenantDomainSerializer(many=True, read_only=True)

    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + ["profile", "settings", "subscription", "domains"]


class TenantTransferOwnershipSerializer(serializers.Serializer):
    new_owner_id = serializers.UUIDField()


class TenantCloneSerializer(serializers.Serializer):
    new_name = serializers.CharField(max_length=150)
    new_slug = serializers.CharField(max_length=100)
    new_code = serializers.CharField(max_length=50, required=False)
    new_owner_id = serializers.UUIDField(required=False)

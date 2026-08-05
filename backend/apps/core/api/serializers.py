"""Public serializers for the core app (identity domain)."""

from __future__ import annotations

from rest_framework import serializers

from apps.core.models import Tenant, User


class UserSerializer(serializers.ModelSerializer):
    """Read-mostly user representation (no password exposure)."""

    full_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "avatar",
            "language",
            "timezone",
            "status",
            "email_verified",
            "phone_verified",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "password_changed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "email_verified",
            "phone_verified",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "password_changed_at",
            "created_at",
            "updated_at",
        )


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "name",
            "code",
            "slug",
            "status",
            "timezone",
            "locale",
            "subscription_tier",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "subscription_tier", "created_at", "updated_at")

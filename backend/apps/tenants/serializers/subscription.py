"""Tenant Subscription serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.tenants.models import TenantSubscription


class TenantSubscriptionSerializer(serializers.ModelSerializer):
    is_active_subscription = serializers.BooleanField(read_only=True)

    class Meta:
        model = TenantSubscription
        fields = [
            "plan",
            "billing_cycle",
            "start_date",
            "end_date",
            "is_trial",
            "grace_period_days",
            "max_users",
            "max_branches",
            "storage_limit_mb",
            "api_rate_limit_per_min",
            "feature_limits",
            "status",
            "is_active_subscription",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "is_active_subscription"]

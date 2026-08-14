"""DRF Serializers for SaaSSubscription."""

from rest_framework import serializers
from apps.saas.models import SaaSSubscription


class SaaSSubscriptionSerializer(serializers.ModelSerializer):
    plan_code = serializers.CharField(source="plan.code", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = SaaSSubscription
        fields = [
            "id",
            "subscription_number",
            "plan_code",
            "plan_name",
            "status",
            "billing_cycle",
            "currency",
            "start_date",
            "trial_end",
            "current_period_start",
            "current_period_end",
            "next_billing_date",
            "cancel_at_period_end",
        ]
        read_only_fields = ["id", "subscription_number", "start_date"]


class SubscriptionUpgradeSerializer(serializers.Serializer):
    new_plan_code = serializers.CharField(max_length=60)

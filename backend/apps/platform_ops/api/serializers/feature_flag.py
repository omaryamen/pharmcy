"""DRF Serializer for GlobalFeatureFlag."""

from rest_framework import serializers
from apps.platform_ops.models import GlobalFeatureFlag


class GlobalFeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalFeatureFlag
        fields = [
            "id",
            "feature_key",
            "name",
            "description",
            "is_globally_enabled",
            "rollout_percentage",
            "target_tiers",
            "whitelisted_tenants",
            "blacklisted_tenants",
        ]
        read_only_fields = ["id"]

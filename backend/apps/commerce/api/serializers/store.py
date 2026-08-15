"""DRF Serializer for TenantStore."""

from rest_framework import serializers
from apps.commerce.models import TenantStore


class TenantStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantStore
        fields = [
            "id",
            "code",
            "name",
            "domain",
            "logo_url",
            "currency",
            "status",
            "is_b2b_enabled",
            "is_b2c_enabled",
            "delivery_fee",
            "free_delivery_threshold",
        ]
        read_only_fields = ["id"]

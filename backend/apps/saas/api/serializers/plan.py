"""DRF Serializers for Plan, PlanFeature, and PlanPrice."""

from rest_framework import serializers
from apps.saas.models import Plan, PlanFeature, PlanPrice, PlanVersion


class PlanPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPrice
        fields = ["id", "billing_cycle", "currency", "price_amount", "setup_fee"]


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ["id", "feature_key", "feature_name", "is_enabled", "limit_value"]


class PlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ["id", "code", "name", "description", "is_active", "is_public", "sort_order", "features", "prices"]

    def get_features(self, obj: Plan):
        current = obj.versions.filter(is_current=True).first()
        if not current:
            return []
        return PlanFeatureSerializer(current.features.all(), many=True).data

    def get_prices(self, obj: Plan):
        current = obj.versions.filter(is_current=True).first()
        if not current:
            return []
        return PlanPriceSerializer(current.prices.all(), many=True).data

"""DRF Serializer for StoreProduct."""

from rest_framework import serializers
from apps.commerce.models import StoreProduct


class StoreProductSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    generic_name = serializers.CharField(source="medicine.generic_name", read_only=True)

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "store",
            "medicine",
            "medicine_name",
            "generic_name",
            "display_name",
            "description",
            "retail_price",
            "b2b_price",
            "is_published",
            "is_featured",
            "is_prescription_required",
            "min_order_qty",
            "max_order_qty",
        ]
        read_only_fields = ["id"]

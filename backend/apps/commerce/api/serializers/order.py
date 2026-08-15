"""DRF Serializer for CommerceOrder and CommerceOrderLine."""

from rest_framework import serializers
from apps.commerce.models import CommerceOrder, CommerceOrderLine


class CommerceOrderLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.display_name", read_only=True)

    class Meta:
        model = CommerceOrderLine
        fields = [
            "id",
            "product",
            "medicine",
            "product_name",
            "quantity",
            "unit_price",
            "discount_amount",
            "tax_amount",
            "total_amount",
        ]
        read_only_fields = ["id"]


class CommerceOrderSerializer(serializers.ModelSerializer):
    lines = CommerceOrderLineSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.display_name", read_only=True)

    class Meta:
        model = CommerceOrder
        fields = [
            "id",
            "order_number",
            "store",
            "customer",
            "customer_name",
            "branch",
            "warehouse",
            "status",
            "payment_status",
            "delivery_method",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "shipping_fee",
            "total_amount",
            "currency",
            "shipping_address",
            "lines",
            "created_at",
        ]
        read_only_fields = ["id", "order_number", "created_at"]

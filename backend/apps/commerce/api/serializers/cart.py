"""DRF Serializer for Cart and CartItem."""

from rest_framework import serializers
from apps.commerce.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.display_name", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "product_name", "quantity", "unit_price"]
        read_only_fields = ["id", "unit_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "store", "customer", "session_key", "currency", "items"]
        read_only_fields = ["id"]

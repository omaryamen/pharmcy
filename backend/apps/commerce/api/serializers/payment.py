"""DRF Serializer for CommercePayment and CommerceRefund."""

from rest_framework import serializers
from apps.commerce.models import CommercePayment, CommerceRefund


class CommerceRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommerceRefund
        fields = ["id", "refund_number", "payment", "amount", "currency", "reason", "created_at"]
        read_only_fields = ["id", "refund_number", "created_at"]


class CommercePaymentSerializer(serializers.ModelSerializer):
    refunds = CommerceRefundSerializer(many=True, read_only=True)

    class Meta:
        model = CommercePayment
        fields = [
            "id",
            "payment_number",
            "order",
            "amount",
            "currency",
            "payment_method",
            "status",
            "external_tx_id",
            "refunds",
            "created_at",
        ]
        read_only_fields = ["id", "payment_number", "created_at"]

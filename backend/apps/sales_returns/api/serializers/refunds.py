"""REST API serializers for Customer Refund processing."""

from rest_framework import serializers

from apps.sales_returns.models import CustomerRefund


class CustomerRefundSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.english_name", read_only=True)
    return_number = serializers.CharField(source="customer_return.return_number", read_only=True)

    class Meta:
        model = CustomerRefund
        fields = [
            "id",
            "refund_number",
            "customer_return",
            "return_number",
            "customer",
            "customer_name",
            "sales_invoice",
            "refund_method",
            "amount",
            "currency",
            "reference_number",
            "status",
            "created_by",
            "approved_by",
            "processed_by",
            "processed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "refund_number", "status", "created_at"]


class CustomerRefundCreateSerializer(serializers.Serializer):
    refund_method = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    reference_number = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

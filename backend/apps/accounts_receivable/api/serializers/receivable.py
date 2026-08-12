"""REST API serializers for CustomerReceivable subledger entity."""

from rest_framework import serializers

from apps.accounts_receivable.models import CustomerReceivable


class CustomerReceivableSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.english_name", read_only=True)
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    sales_invoice_number = serializers.CharField(source="sales_invoice.invoice_number", read_only=True, default=None)

    class Meta:
        model = CustomerReceivable
        fields = [
            "id",
            "receivable_number",
            "company",
            "branch",
            "customer",
            "customer_name",
            "customer_code",
            "sales_invoice",
            "sales_invoice_number",
            "original_amount",
            "paid_amount",
            "credit_amount",
            "refund_amount",
            "adjusted_amount",
            "outstanding_amount",
            "currency",
            "exchange_rate",
            "invoice_date",
            "due_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "receivable_number", "status", "created_at", "updated_at"]


class SyncReceivableSerializer(serializers.Serializer):
    sales_invoice_id = serializers.UUIDField()
    due_days = serializers.IntegerField(required=False, default=30)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, default="")

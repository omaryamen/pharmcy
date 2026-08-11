"""REST API serializers for Customer Return documents and inspection."""

from rest_framework import serializers

from apps.sales_returns.models import CustomerReturn, CustomerReturnLine


class CustomerReturnLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    storage_location_name = serializers.CharField(source="storage_location.name", read_only=True)

    class Meta:
        model = CustomerReturnLine
        fields = [
            "id",
            "customer_return",
            "sales_invoice_line",
            "medicine",
            "medicine_name",
            "batch",
            "batch_number",
            "warehouse",
            "storage_location",
            "storage_location_name",
            "original_sold_quantity",
            "previously_returned_quantity",
            "returnable_quantity",
            "requested_return_quantity",
            "accepted_return_quantity",
            "rejected_return_quantity",
            "unit",
            "original_unit_price",
            "refund_unit_price",
            "discount_amount",
            "tax_amount",
            "refund_line_total",
            "condition",
            "return_reason",
            "inspection_result",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CustomerReturnSerializer(serializers.ModelSerializer):
    lines = CustomerReturnLineSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    customer_name = serializers.CharField(source="customer.english_name", read_only=True)
    invoice_number = serializers.CharField(source="sales_invoice.invoice_number", read_only=True)

    class Meta:
        model = CustomerReturn
        fields = [
            "id",
            "return_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "warehouse",
            "warehouse_name",
            "customer",
            "customer_name",
            "sales_invoice",
            "invoice_number",
            "return_date",
            "status",
            "return_reason",
            "currency",
            "exchange_rate",
            "subtotal",
            "discount",
            "tax",
            "refund_amount",
            "store_credit_amount",
            "created_by",
            "approved_by",
            "inspected_by",
            "processed_by",
            "approved_at",
            "completed_at",
            "notes",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "return_number", "status", "created_at", "updated_at"]


class CustomerReturnLineCreateSerializer(serializers.Serializer):
    sales_invoice_line_id = serializers.UUIDField()
    requested_return_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)
    condition = serializers.CharField(required=False, default="sealed")
    return_reason = serializers.CharField(required=False, default="other")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class CustomerReturnCreateSerializer(serializers.Serializer):
    sales_invoice_id = serializers.UUIDField()
    return_reason = serializers.CharField(required=False, default="other")
    lines = CustomerReturnLineCreateSerializer(many=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ReturnInspectionLineDataSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    accepted_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)
    rejected_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default=0)
    condition = serializers.CharField(required=False, default="sealed")
    inspection_result = serializers.CharField(required=False, default="accepted")


class ReturnInspectionSerializer(serializers.Serializer):
    inspection_lines = ReturnInspectionLineDataSerializer(many=True)

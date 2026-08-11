"""REST API serializers for SalesInvoice and SalesPayment entities."""

from rest_framework import serializers

from apps.sales.models import SalesInvoice, SalesInvoiceLine, SalesPayment


class SalesInvoiceLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    batch_number = serializers.ReadOnlyField(source="batch.batch_number")
    storage_location_name = serializers.ReadOnlyField(source="storage_location.name")

    class Meta:
        model = SalesInvoiceLine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "batch",
            "batch_number",
            "warehouse",
            "storage_location",
            "storage_location_name",
            "quantity",
            "unit",
            "unit_price",
            "discount_percentage",
            "discount_amount",
            "tax_percentage",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "cost_price",
            "profit_amount",
            "notes",
        ]
        read_only_fields = ["id", "line_subtotal", "line_total", "cost_price", "profit_amount"]


class SalesPaymentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")

    class Meta:
        model = SalesPayment
        fields = [
            "id",
            "payment_number",
            "sales_invoice",
            "payment_method",
            "amount",
            "tendered_amount",
            "change_amount",
            "currency",
            "reference_number",
            "status",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "payment_number", "change_amount", "created_at"]


class SalesInvoiceSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    customer_name = serializers.ReadOnlyField(source="customer.legal_name")
    cashier_name = serializers.ReadOnlyField(source="cashier.get_full_name")
    lines = SalesInvoiceLineSerializer(many=True, read_only=True)
    payments = SalesPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            "id",
            "invoice_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "warehouse",
            "warehouse_name",
            "customer",
            "customer_name",
            "register_session",
            "invoice_date",
            "invoice_time",
            "status",
            "payment_status",
            "currency",
            "exchange_rate",
            "subtotal",
            "discount",
            "tax",
            "other_charges",
            "grand_total",
            "paid_amount",
            "change_amount",
            "outstanding_amount",
            "idempotency_key",
            "cashier",
            "cashier_name",
            "salesperson",
            "completed_at",
            "cancelled_at",
            "notes",
            "lines",
            "payments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "invoice_date",
            "invoice_time",
            "status",
            "payment_status",
            "subtotal",
            "grand_total",
            "paid_amount",
            "change_amount",
            "outstanding_amount",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

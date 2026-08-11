"""REST API serializers for GoodsReceipt entities."""

from rest_framework import serializers

from apps.goods_receipt.models import GoodsReceipt, GoodsReceiptLine


class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    storage_location_name = serializers.ReadOnlyField(source="storage_location.name")

    class Meta:
        model = GoodsReceiptLine
        fields = [
            "id",
            "purchase_order_line",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "batch",
            "batch_number",
            "manufacturing_date",
            "expiry_date",
            "received_quantity",
            "accepted_quantity",
            "rejected_quantity",
            "damaged_quantity",
            "free_quantity",
            "unit",
            "unit_cost",
            "discount",
            "tax",
            "total_cost",
            "storage_location",
            "storage_location_name",
            "quality_status",
            "temperature_at_receipt",
            "min_temperature",
            "max_temperature",
            "temperature_excursion_flag",
            "inspection_result",
            "notes",
        ]
        read_only_fields = [
            "id",
            "batch",
            "total_cost",
            "temperature_excursion_flag",
        ]


class GoodsReceiptSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    po_number = serializers.ReadOnlyField(source="purchase_order.po_number")
    received_by_name = serializers.ReadOnlyField(source="received_by.get_full_name")
    verified_by_name = serializers.ReadOnlyField(source="verified_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")
    lines = GoodsReceiptLineSerializer(many=True, read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = [
            "id",
            "receipt_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "supplier",
            "supplier_name",
            "purchase_order",
            "po_number",
            "warehouse",
            "warehouse_name",
            "receiving_location",
            "supplier_delivery_number",
            "supplier_invoice_reference",
            "receipt_date",
            "delivery_date",
            "status",
            "currency",
            "exchange_rate",
            "subtotal",
            "discount",
            "tax",
            "shipping_cost",
            "other_charges",
            "grand_total",
            "idempotency_key",
            "received_by",
            "received_by_name",
            "verified_by",
            "verified_by_name",
            "approved_by",
            "approved_by_name",
            "completed_at",
            "notes",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "receipt_number",
            "status",
            "subtotal",
            "discount",
            "tax",
            "grand_total",
            "received_by",
            "verified_by",
            "approved_by",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class GoodsReceiptReverseRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)

"""REST API serializers for PurchaseOrder entities."""

from rest_framework import serializers

from apps.procurement.models import PurchaseOrder, PurchaseOrderAmendment, PurchaseOrderLine


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    remaining_quantity = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderLine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "warehouse",
            "warehouse_name",
            "storage_location",
            "supplier_product_code",
            "supplier_barcode",
            "description",
            "ordered_quantity",
            "free_quantity",
            "unit",
            "unit_price",
            "discount_percentage",
            "discount_amount",
            "tax_percentage",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "received_quantity",
            "free_quantity_received",
            "remaining_quantity",
            "expected_date",
            "notes",
        ]
        read_only_fields = [
            "id",
            "discount_amount",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "received_quantity",
            "free_quantity_received",
            "remaining_quantity",
        ]


class PurchaseOrderAmendmentSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.ReadOnlyField(source="changed_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")

    class Meta:
        model = PurchaseOrderAmendment
        fields = [
            "id",
            "amendment_number",
            "reason",
            "changed_fields",
            "status",
            "changed_by",
            "changed_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
        ]
        read_only_fields = ["id", "amendment_number", "created_at"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)
    amendments = PurchaseOrderAmendmentSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "supplier",
            "supplier_name",
            "warehouse",
            "warehouse_name",
            "requisition",
            "supplier_reference",
            "order_date",
            "expected_delivery_date",
            "actual_delivery_date",
            "currency",
            "exchange_rate",
            "payment_terms",
            "status",
            "priority",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "shipping_cost",
            "other_charges",
            "grand_total",
            "notes",
            "terms_and_conditions",
            "idempotency_key",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "sent_at",
            "acknowledged_at",
            "cancelled_by",
            "cancelled_at",
            "cancellation_reason",
            "lines",
            "amendments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "po_number",
            "status",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "grand_total",
            "created_by",
            "approved_by",
            "approved_at",
            "sent_at",
            "acknowledged_at",
            "cancelled_by",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class PurchaseOrderAmendRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
    changes = serializers.JSONField(required=True)


class PurchaseOrderCancelRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)

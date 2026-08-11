"""REST API serializers for PurchaseReturn entities."""

from rest_framework import serializers

from apps.purchase_returns.models import PurchaseReturn, PurchaseReturnLine, ReturnDiscrepancy, SupplierCreditNote


class PurchaseReturnLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    batch_number = serializers.ReadOnlyField(source="batch.batch_number")
    storage_location_name = serializers.ReadOnlyField(source="storage_location.name")

    class Meta:
        model = PurchaseReturnLine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "batch",
            "batch_number",
            "goods_receipt_line",
            "purchase_order_line",
            "storage_location",
            "storage_location_name",
            "available_quantity",
            "requested_return_quantity",
            "approved_return_quantity",
            "dispatched_quantity",
            "supplier_accepted_quantity",
            "supplier_rejected_quantity",
            "damaged_quantity",
            "unit",
            "unit_cost",
            "discount",
            "tax",
            "total_value",
            "return_reason",
            "condition",
            "notes",
        ]
        read_only_fields = [
            "id",
            "dispatched_quantity",
            "supplier_accepted_quantity",
            "supplier_rejected_quantity",
            "total_value",
        ]


class ReturnDiscrepancySerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")

    class Meta:
        model = ReturnDiscrepancy
        fields = [
            "id",
            "discrepancy_number",
            "return_line",
            "expected_quantity",
            "dispatched_quantity",
            "supplier_accepted_quantity",
            "supplier_rejected_quantity",
            "difference",
            "reason",
            "evidence",
            "status",
            "created_by",
            "created_by_name",
            "resolution",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "discrepancy_number", "created_at"]


class SupplierCreditNoteSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")

    class Meta:
        model = SupplierCreditNote
        fields = [
            "id",
            "credit_note_number",
            "supplier",
            "supplier_name",
            "supplier_reference",
            "accepted_value",
            "tax_value",
            "net_credit_value",
            "currency",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "credit_note_number", "created_at"]


class PurchaseReturnSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    requested_by_name = serializers.ReadOnlyField(source="requested_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")
    lines = PurchaseReturnLineSerializer(many=True, read_only=True)
    discrepancies = ReturnDiscrepancySerializer(many=True, read_only=True)
    credit_notes = SupplierCreditNoteSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseReturn
        fields = [
            "id",
            "return_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "supplier",
            "supplier_name",
            "purchase_order",
            "goods_receipt",
            "warehouse",
            "warehouse_name",
            "return_date",
            "status",
            "return_reason",
            "priority",
            "currency",
            "exchange_rate",
            "subtotal",
            "discount",
            "tax",
            "other_charges",
            "grand_total",
            "idempotency_key",
            "requested_by",
            "requested_by_name",
            "approved_by",
            "approved_by_name",
            "dispatched_by",
            "received_by",
            "approved_at",
            "dispatched_at",
            "completed_at",
            "notes",
            "lines",
            "discrepancies",
            "credit_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "return_number",
            "status",
            "subtotal",
            "discount",
            "tax",
            "grand_total",
            "requested_by",
            "approved_by",
            "dispatched_by",
            "received_by",
            "approved_at",
            "dispatched_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class SupplierAcceptanceRequestSerializer(serializers.Serializer):
    supplier_reference = serializers.CharField(required=False, allow_blank=True)
    line_acceptances = serializers.ListField(child=serializers.DictField())

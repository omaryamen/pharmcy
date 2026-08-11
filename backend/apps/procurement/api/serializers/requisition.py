"""REST API serializers for PurchaseRequisition entities."""

from rest_framework import serializers

from apps.procurement.models import PurchaseRequisition, PurchaseRequisitionLine


class PurchaseRequisitionLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    preferred_supplier_name = serializers.ReadOnlyField(source="preferred_supplier.legal_name")

    class Meta:
        model = PurchaseRequisitionLine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "preferred_supplier",
            "preferred_supplier_name",
            "requested_quantity",
            "approved_quantity",
            "unit",
            "estimated_unit_cost",
            "estimated_total_cost",
            "required_date",
            "notes",
        ]
        read_only_fields = ["id", "estimated_total_cost"]


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    requested_by_name = serializers.ReadOnlyField(source="requested_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")
    lines = PurchaseRequisitionLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
            "requisition_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "warehouse",
            "warehouse_name",
            "department",
            "priority",
            "reason",
            "status",
            "required_date",
            "requested_by",
            "requested_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "rejection_reason",
            "notes",
            "total_estimated_cost",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requisition_number",
            "status",
            "total_estimated_cost",
            "requested_by",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "created_at",
            "updated_at",
        ]

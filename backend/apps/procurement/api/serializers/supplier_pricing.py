"""REST API serializers for SupplierProductPrice entities."""

from rest_framework import serializers

from apps.procurement.models import SupplierProductPrice


class SupplierProductPriceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")

    class Meta:
        model = SupplierProductPrice
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "supplier_sku",
            "supplier_barcode",
            "last_purchase_price",
            "current_contract_price",
            "minimum_order_quantity",
            "maximum_order_quantity",
            "is_preferred_supplier",
            "lead_time_days",
            "currency",
            "effective_date",
            "expiry_date",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

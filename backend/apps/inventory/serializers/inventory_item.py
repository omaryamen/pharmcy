"""Serializers for InventoryItem entity and stock adjustment operations."""

from __future__ import annotations

from rest_framework import serializers

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.inventory.models import AdjustmentReason, Batch, InventoryItem, TransactionType
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse


class InventoryItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    expiry_date = serializers.DateField(source="batch.expiry_date", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    location_code = serializers.CharField(source="storage_location.code", read_only=True)
    available_quantity = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_cost_value = serializers.DecimalField(max_digits=14, decimal_places=4, read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "tenant",
            "company",
            "branch",
            "warehouse",
            "warehouse_name",
            "storage_location",
            "location_code",
            "medicine",
            "medicine_name",
            "medicine_code",
            "batch",
            "batch_number",
            "expiry_date",
            "status",
            "on_hand_quantity",
            "reserved_quantity",
            "available_quantity",
            "damaged_quantity",
            "quarantine_quantity",
            "unit_cost",
            "average_cost",
            "last_cost",
            "selling_price",
            "total_cost_value",
            "min_quantity",
            "max_quantity",
            "reorder_point",
            "last_movement_date",
            "last_count_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "medicine_name",
            "medicine_code",
            "batch_number",
            "expiry_date",
            "warehouse_name",
            "location_code",
            "available_quantity",
            "total_cost_value",
            "created_at",
            "updated_at",
        ]


class InventoryItemDetailSerializer(InventoryItemSerializer):
    class Meta(InventoryItemSerializer.Meta):
        pass


class InventoryItemCreateSerializer(serializers.Serializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    storage_location = serializers.PrimaryKeyRelatedField(queryset=StorageLocation.objects.all())
    medicine = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.all())
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())

    unit_cost = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default=0.0000)
    selling_price = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default=0.0000)
    min_quantity = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=0.00)
    max_quantity = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=0.00)
    reorder_point = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=0.00)


class StockAdjustmentSerializer(serializers.Serializer):
    quantity_delta = serializers.DecimalField(max_digits=14, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=TransactionType.choices, default=TransactionType.ADJUSTMENT_INCREASE)
    reason = serializers.ChoiceField(choices=AdjustmentReason.choices, default=AdjustmentReason.CORRECTION)
    reference_number = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    unit_cost = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class StockReservationSerializer(serializers.Serializer):
    requested_quantity = serializers.DecimalField(max_digits=14, decimal_places=2)
    reference_number = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

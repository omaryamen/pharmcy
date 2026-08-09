"""Serializers for InventoryTransaction audit log entity."""

from __future__ import annotations

from rest_framework import serializers

from apps.inventory.models import InventoryTransaction


class InventoryTransactionSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    location_code = serializers.CharField(source="storage_location.code", read_only=True)
    performed_by_username = serializers.CharField(source="performed_by.username", read_only=True)

    class Meta:
        model = InventoryTransaction
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
            "batch",
            "batch_number",
            "inventory_item",
            "transaction_type",
            "quantity",
            "unit_cost",
            "total_cost",
            "quantity_before",
            "quantity_after",
            "reference_number",
            "reason",
            "performed_by",
            "performed_by_username",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "medicine_name",
            "batch_number",
            "warehouse_name",
            "location_code",
            "performed_by_username",
            "created_at",
        ]

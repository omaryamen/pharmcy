"""Serializers for StockTransferLine entity."""

from __future__ import annotations

from rest_framework import serializers

from apps.stock_transfer.models import StockTransferLine


class StockTransferLineSerializer(serializers.ModelSerializer):
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True, default="")
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, default="")
    destination_location_code = serializers.CharField(source="destination_location.code", read_only=True, default="")

    class Meta:
        model = StockTransferLine
        fields = [
            "id",
            "medicine",
            "medicine_code",
            "medicine_name",
            "batch",
            "batch_number",
            "source_location",
            "source_location_code",
            "destination_location",
            "destination_location_code",
            "requested_quantity",
            "approved_quantity",
            "picked_quantity",
            "dispatched_quantity",
            "received_quantity",
            "rejected_quantity",
            "damaged_quantity",
            "unit",
            "unit_cost",
            "total_cost",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "total_cost", "status", "created_at"]


class StockTransferLineCreateSerializer(serializers.Serializer):
    medicine_id = serializers.UUIDField()
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    source_location_id = serializers.UUIDField(required=False, allow_null=True)
    destination_location_id = serializers.UUIDField(required=False, allow_null=True)
    requested_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)
    unit = serializers.CharField(max_length=50, required=False, default="Pcs")
    unit_cost = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default="0.0000")
    notes = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)

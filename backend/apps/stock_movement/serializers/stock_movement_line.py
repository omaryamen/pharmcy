"""Serializers for StockMovementLine entity."""

from rest_framework import serializers

from apps.stock_movement.models import StockMovementLine


class StockMovementLineSerializer(serializers.ModelSerializer):
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True, default="")
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, default="")
    destination_location_code = serializers.CharField(source="destination_location.code", read_only=True, default="")

    class Meta:
        model = StockMovementLine
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
            "quantity",
            "unit",
            "unit_cost",
            "total_cost",
            "reason",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "total_cost", "created_at"]


class StockMovementLineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovementLine
        fields = [
            "medicine",
            "batch",
            "source_location",
            "destination_location",
            "quantity",
            "unit",
            "unit_cost",
            "reason",
            "notes",
        ]

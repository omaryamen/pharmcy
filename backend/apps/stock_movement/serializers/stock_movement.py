"""Serializers for StockMovement entity and operational endpoints."""

from rest_framework import serializers

from apps.stock_movement.models import StockMovement
from apps.stock_movement.serializers.stock_movement_line import StockMovementLineCreateSerializer, StockMovementLineSerializer


class StockMovementSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    source_warehouse_name = serializers.CharField(source="source_warehouse.name", read_only=True, default="")
    destination_warehouse_name = serializers.CharField(source="destination_warehouse.name", read_only=True, default="")
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, default="")
    destination_location_code = serializers.CharField(source="destination_location.code", read_only=True, default="")
    performed_by_name = serializers.CharField(source="performed_by.email", read_only=True, default="")
    approved_by_name = serializers.CharField(source="approved_by.email", read_only=True, default="")
    lines = StockMovementLineSerializer(many=True, read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "movement_number",
            "company",
            "company_name",
            "branch",
            "warehouse",
            "warehouse_code",
            "warehouse_name",
            "source_warehouse",
            "source_warehouse_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "source_location",
            "source_location_code",
            "destination_location",
            "destination_location_code",
            "medicine",
            "batch",
            "movement_type",
            "movement_status",
            "quantity",
            "unit_of_measure",
            "unit_cost",
            "total_cost",
            "reference_type",
            "reference_id",
            "reference_number",
            "reason",
            "notes",
            "performed_by",
            "performed_by_name",
            "approved_by",
            "approved_by_name",
            "reversed_movement",
            "is_reversal",
            "idempotency_key",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
            "lines",
        ]
        read_only_fields = [
            "id",
            "movement_number",
            "movement_status",
            "total_cost",
            "reversed_movement",
            "is_reversal",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class StockMovementCreateSerializer(serializers.ModelSerializer):
    lines = StockMovementLineCreateSerializer(many=True, required=False)
    auto_process = serializers.BooleanField(default=False)

    class Meta:
        model = StockMovement
        fields = [
            "company",
            "branch",
            "warehouse",
            "source_warehouse",
            "destination_warehouse",
            "source_location",
            "destination_location",
            "medicine",
            "batch",
            "movement_type",
            "quantity",
            "unit_of_measure",
            "unit_cost",
            "reference_type",
            "reference_id",
            "reference_number",
            "reason",
            "notes",
            "idempotency_key",
            "lines",
            "auto_process",
        ]


class StockMovementReverseSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, default="")


class ReceiveStockOperationSerializer(serializers.Serializer):
    company = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    location = serializers.UUIDField()
    medicine = serializers.UUIDField()
    batch = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=14, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=14, decimal_places=4, default="0.0000")
    reference_number = serializers.CharField(max_length=100, required=False, default="")
    idempotency_key = serializers.CharField(max_length=100, required=False, default="")


class IssueStockOperationSerializer(serializers.Serializer):
    company = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    location = serializers.UUIDField()
    medicine = serializers.UUIDField()
    batch = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=14, decimal_places=2)
    reference_number = serializers.CharField(max_length=100, required=False, default="")
    idempotency_key = serializers.CharField(max_length=100, required=False, default="")


class TransferStockOperationSerializer(serializers.Serializer):
    company = serializers.UUIDField()
    source_warehouse = serializers.UUIDField()
    destination_warehouse = serializers.UUIDField()
    source_location = serializers.UUIDField()
    destination_location = serializers.UUIDField()
    medicine = serializers.UUIDField()
    batch = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=14, decimal_places=2)
    reference_number = serializers.CharField(max_length=100, required=False, default="")
    idempotency_key = serializers.CharField(max_length=100, required=False, default="")

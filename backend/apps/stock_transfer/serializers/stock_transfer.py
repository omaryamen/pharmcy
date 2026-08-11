"""Serializers for StockTransfer master entity and action requests."""

from __future__ import annotations

from rest_framework import serializers

from apps.stock_transfer.models import StockTransfer, StockTransferHistory
from apps.stock_transfer.serializers.stock_transfer_discrepancy import StockTransferDiscrepancySerializer
from apps.stock_transfer.serializers.stock_transfer_line import (
    StockTransferLineCreateSerializer,
    StockTransferLineSerializer,
)


class StockTransferHistorySerializer(serializers.ModelSerializer):
    performed_by_email = serializers.CharField(source="performed_by.email", read_only=True, default="")

    class Meta:
        model = StockTransferHistory
        fields = ["id", "event_type", "performed_by", "performed_by_email", "timestamp", "details"]


class StockTransferSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    source_warehouse_name = serializers.CharField(source="source_warehouse.name", read_only=True)
    destination_warehouse_name = serializers.CharField(source="destination_warehouse.name", read_only=True)
    source_branch_name = serializers.CharField(source="source_branch.name", read_only=True, default="")
    destination_branch_name = serializers.CharField(source="destination_branch.name", read_only=True, default="")
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, default="")
    destination_location_code = serializers.CharField(source="destination_location.code", read_only=True, default="")

    requested_by_email = serializers.CharField(source="requested_by.email", read_only=True, default="")
    approved_by_email = serializers.CharField(source="approved_by.email", read_only=True, default="")
    dispatched_by_email = serializers.CharField(source="dispatched_by.email", read_only=True, default="")
    received_by_email = serializers.CharField(source="received_by.email", read_only=True, default="")

    lines = StockTransferLineSerializer(many=True, read_only=True)
    discrepancies = StockTransferDiscrepancySerializer(many=True, read_only=True)
    history = StockTransferHistorySerializer(many=True, read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            "id",
            "transfer_number",
            "company",
            "company_name",
            "source_branch",
            "source_branch_name",
            "destination_branch",
            "destination_branch_name",
            "source_warehouse",
            "source_warehouse_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "source_location",
            "source_location_code",
            "destination_location",
            "destination_location_code",
            "transfer_type",
            "priority",
            "status",
            "requested_by",
            "requested_by_email",
            "approved_by",
            "approved_by_email",
            "dispatched_by",
            "dispatched_by_email",
            "received_by",
            "received_by_email",
            "requested_at",
            "approved_at",
            "dispatched_at",
            "received_at",
            "expected_arrival_date",
            "actual_arrival_date",
            "reason",
            "notes",
            "reference_type",
            "reference_id",
            "total_items",
            "total_requested_quantity",
            "total_dispatched_quantity",
            "total_received_quantity",
            "total_cost",
            "idempotency_key",
            "has_discrepancy",
            "lines",
            "discrepancies",
            "history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "transfer_number",
            "status",
            "total_items",
            "total_requested_quantity",
            "total_dispatched_quantity",
            "total_received_quantity",
            "total_cost",
            "has_discrepancy",
            "created_at",
            "updated_at",
        ]


class StockTransferCreateSerializer(serializers.Serializer):
    company = serializers.UUIDField()
    source_warehouse = serializers.UUIDField()
    destination_warehouse = serializers.UUIDField()
    source_branch = serializers.UUIDField(required=False, allow_null=True)
    destination_branch = serializers.UUIDField(required=False, allow_null=True)
    source_location = serializers.UUIDField(required=False, allow_null=True)
    destination_location = serializers.UUIDField(required=False, allow_null=True)
    transfer_type = serializers.CharField(required=False, default="warehouse_transfer")
    priority = serializers.CharField(required=False, default="medium")
    expected_arrival_date = serializers.DateField(required=False, allow_null=True)
    reason = serializers.CharField(max_length=255, required=False, default="", allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, default="", allow_blank=True)
    reference_type = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)
    reference_id = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    idempotency_key = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    lines = StockTransferLineCreateSerializer(many=True)


class StockTransferApproveLineSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    approved_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)


class StockTransferApproveSerializer(serializers.Serializer):
    lines = StockTransferApproveLineSerializer(many=True, required=False)


class StockTransferPickLineSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    picked_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)


class StockTransferPickSerializer(serializers.Serializer):
    lines = StockTransferPickLineSerializer(many=True, required=False)


class StockTransferDispatchLineSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    dispatched_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)


class StockTransferDispatchSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    lines = StockTransferDispatchLineSerializer(many=True, required=False)


class StockTransferReceiveLineSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    destination_location_id = serializers.UUIDField(required=False, allow_null=True)
    received_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default="0.0000")
    damaged_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default="0.0000")
    rejected_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, default="0.0000")
    received_medicine_id = serializers.UUIDField(required=False, allow_null=True)
    received_batch_id = serializers.UUIDField(required=False, allow_null=True)
    damage_reason = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)


class StockTransferReceiveSerializer(serializers.Serializer):
    lines = StockTransferReceiveLineSerializer(many=True)


class StockTransferCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)


class StockTransferReverseSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)

"""Serializers for StockCount entity and action payloads."""

from __future__ import annotations

from rest_framework import serializers

from apps.stock_adjustment.models import StockCount, StockCountHistory
from apps.stock_adjustment.serializers.stock_count_line import StockCountLineRecordSerializer, StockCountLineSerializer


class StockCountHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source="performed_by.email", read_only=True, default="")

    class Meta:
        model = StockCountHistory
        fields = ["id", "event_type", "performed_by", "performed_by_name", "details", "timestamp"]


class StockCountSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    storage_location_code = serializers.CharField(source="storage_location.code", read_only=True, default="")
    created_by_name = serializers.CharField(source="created_by.email", read_only=True, default="")
    approved_by_name = serializers.CharField(source="approved_by.email", read_only=True, default="")
    reconciled_by_name = serializers.CharField(source="reconciled_by.email", read_only=True, default="")
    lines = StockCountLineSerializer(many=True, read_only=True)

    class Meta:
        model = StockCount
        fields = [
            "id",
            "count_number",
            "company",
            "company_name",
            "branch",
            "warehouse",
            "warehouse_code",
            "warehouse_name",
            "storage_location",
            "storage_location_code",
            "count_type",
            "count_status",
            "count_scope_type",
            "scope_filter",
            "is_blind_count",
            "freeze_inventory",
            "snapshot_at",
            "started_at",
            "submitted_at",
            "reviewed_at",
            "approved_at",
            "reconciled_at",
            "cancelled_at",
            "created_by",
            "created_by_name",
            "started_by",
            "completed_by",
            "reviewed_by",
            "approved_by",
            "approved_by_name",
            "reconciled_by",
            "reconciled_by_name",
            "reason",
            "notes",
            "total_items_counted",
            "total_shortage_quantity",
            "total_overage_quantity",
            "total_variance_cost",
            "idempotency_key",
            "created_at",
            "updated_at",
            "lines",
        ]
        read_only_fields = [
            "id",
            "count_number",
            "count_status",
            "snapshot_at",
            "started_at",
            "submitted_at",
            "reviewed_at",
            "approved_at",
            "reconciled_at",
            "cancelled_at",
            "total_items_counted",
            "total_shortage_quantity",
            "total_overage_quantity",
            "total_variance_cost",
            "created_at",
            "updated_at",
        ]


class StockCountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockCount
        fields = [
            "company",
            "branch",
            "warehouse",
            "storage_location",
            "count_type",
            "count_scope_type",
            "scope_filter",
            "is_blind_count",
            "freeze_inventory",
            "reason",
            "notes",
            "idempotency_key",
        ]


class StockCountRecordLinesSerializer(serializers.Serializer):
    lines = StockCountLineRecordSerializer(many=True)


class StockCountRecountRequestSerializer(serializers.Serializer):
    line_ids = serializers.ListField(child=serializers.UUIDField())
    reason = serializers.CharField(max_length=255)


class StockCountRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)


class StockCountReconcileSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=100, required=False, default="")

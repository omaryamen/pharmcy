"""Serializers for StockTransferDiscrepancy entity."""

from __future__ import annotations

from rest_framework import serializers

from apps.stock_transfer.models import StockTransferDiscrepancy


class StockTransferDiscrepancySerializer(serializers.ModelSerializer):
    transfer_number = serializers.CharField(source="stock_transfer.transfer_number", read_only=True)
    expected_batch_number = serializers.CharField(source="expected_batch.batch_number", read_only=True, default="")
    received_batch_number = serializers.CharField(source="received_batch.batch_number", read_only=True, default="")
    expected_medicine_name = serializers.CharField(source="expected_medicine.english_name", read_only=True, default="")
    received_medicine_name = serializers.CharField(source="received_medicine.english_name", read_only=True, default="")
    reported_by_email = serializers.CharField(source="reported_by.email", read_only=True, default="")
    reviewed_by_email = serializers.CharField(source="reviewed_by.email", read_only=True, default="")

    class Meta:
        model = StockTransferDiscrepancy
        fields = [
            "id",
            "discrepancy_number",
            "stock_transfer",
            "transfer_number",
            "transfer_line",
            "discrepancy_type",
            "expected_quantity",
            "actual_quantity",
            "difference_quantity",
            "expected_batch",
            "expected_batch_number",
            "received_batch",
            "received_batch_number",
            "expected_medicine",
            "expected_medicine_name",
            "received_medicine",
            "received_medicine_name",
            "reason",
            "evidence",
            "status",
            "reported_by",
            "reported_by_email",
            "reviewed_by",
            "reviewed_by_email",
            "resolution",
            "resolution_date",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "discrepancy_number",
            "stock_transfer",
            "created_at",
        ]


class DiscrepancyResolveSerializer(serializers.Serializer):
    resolution = serializers.CharField(max_length=1000)

"""REST API serializers for InventoryAlert entities."""

from rest_framework import serializers

from apps.alerts.models import InventoryAlert


class InventoryAlertSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    storage_location_name = serializers.ReadOnlyField(source="storage_location.name")
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    batch_number = serializers.ReadOnlyField(source="batch.batch_number")
    acknowledged_by_name = serializers.ReadOnlyField(source="acknowledged_by.get_full_name")
    resolved_by_name = serializers.ReadOnlyField(source="resolved_by.get_full_name")

    class Meta:
        model = InventoryAlert
        fields = [
            "id",
            "alert_number",
            "company",
            "company_name",
            "warehouse",
            "warehouse_name",
            "storage_location",
            "storage_location_name",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "batch",
            "batch_number",
            "alert_type",
            "severity",
            "status",
            "title",
            "message",
            "current_value",
            "threshold_value",
            "triggered_at",
            "acknowledged_at",
            "acknowledged_by",
            "acknowledged_by_name",
            "resolved_at",
            "resolved_by",
            "resolved_by_name",
            "resolution_notes",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "alert_number",
            "triggered_at",
            "acknowledged_at",
            "acknowledged_by",
            "resolved_at",
            "resolved_by",
            "created_at",
            "updated_at",
        ]


class AlertResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=False, allow_blank=True, default="")


class AlertScanRequestSerializer(serializers.Serializer):
    near_expiry_days = serializers.IntegerField(required=False, default=90, min_value=1)
    critical_expiry_days = serializers.IntegerField(required=False, default=30, min_value=1)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)

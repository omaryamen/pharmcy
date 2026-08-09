"""Serializers for StockCountLine entity with Blind Count masking logic."""

from __future__ import annotations

from rest_framework import serializers

from apps.stock_adjustment.models import StockCountLine
from apps.stock_adjustment.permissions import CanViewSystemQuantity


class StockCountLineSerializer(serializers.ModelSerializer):
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True, default="")
    storage_location_code = serializers.CharField(source="storage_location.code", read_only=True, default="")
    counted_by_name = serializers.CharField(source="counted_by.email", read_only=True, default="")

    snapshot_quantity = serializers.SerializerMethodField()
    variance_quantity = serializers.SerializerMethodField()
    variance_percentage = serializers.SerializerMethodField()
    variance_cost = serializers.SerializerMethodField()

    class Meta:
        model = StockCountLine
        fields = [
            "id",
            "medicine",
            "medicine_code",
            "medicine_name",
            "batch",
            "batch_number",
            "storage_location",
            "storage_location_code",
            "unit",
            "unit_cost",
            "snapshot_quantity",
            "counted_quantity",
            "variance_quantity",
            "variance_percentage",
            "variance_cost",
            "variance_direction",
            "count_status",
            "counted_by",
            "counted_by_name",
            "counted_at",
            "notes",
            "recount_requested",
            "recount_quantity",
            "created_at",
        ]
        read_only_fields = ["id", "variance_direction", "created_at"]

    def _should_hide_system_quantity(self) -> bool:
        request = self.context.get("request")
        if not request:
            return False

        user = getattr(request, "user", None)
        if user and getattr(user, "is_superuser", False):
            return False

        count = getattr(self.instance, "stock_count", None)
        if not count:
            return False

        # Blind count masking: if is_blind_count is True and status is IN_PROGRESS, or user lacks CanViewSystemQuantity
        if count.is_blind_count and count.count_status in ["in_progress", "draft"]:
            return True

        if not CanViewSystemQuantity().has_permission(request, None) and count.is_blind_count:
            return True

        return False

    def get_snapshot_quantity(self, obj: StockCountLine):
        if self._should_hide_system_quantity():
            return None
        return str(obj.snapshot_quantity)

    def get_variance_quantity(self, obj: StockCountLine):
        if self._should_hide_system_quantity():
            return None
        return str(obj.variance_quantity)

    def get_variance_percentage(self, obj: StockCountLine):
        if self._should_hide_system_quantity():
            return None
        return str(obj.variance_percentage)

    def get_variance_cost(self, obj: StockCountLine):
        if self._should_hide_system_quantity():
            return None
        return str(obj.variance_cost)


class StockCountLineRecordSerializer(serializers.Serializer):
    line_id = serializers.UUIDField()
    counted_quantity = serializers.DecimalField(max_digits=14, decimal_places=2)
    notes = serializers.CharField(max_length=255, required=False, default="")

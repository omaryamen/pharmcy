"""Admin registrations for Enterprise Stock Movement Engine."""

from django.contrib import admin

from apps.stock_movement.models import StockMovement, StockMovementLine


class StockMovementLineInline(admin.TabularInline):
    model = StockMovementLine
    extra = 0
    raw_id_fields = ["medicine", "batch", "source_location", "destination_location"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        "movement_number",
        "tenant",
        "company",
        "warehouse",
        "movement_type",
        "movement_status",
        "quantity",
        "total_cost",
        "created_at",
    ]
    list_filter = ["tenant", "movement_type", "movement_status", "is_reversal", "created_at"]
    search_fields = ["movement_number", "reference_number", "idempotency_key", "reason"]
    raw_id_fields = [
        "tenant",
        "company",
        "branch",
        "warehouse",
        "source_warehouse",
        "destination_warehouse",
        "source_location",
        "destination_location",
        "medicine",
        "batch",
        "performed_by",
        "approved_by",
        "reversed_movement",
    ]
    inlines = [StockMovementLineInline]


@admin.register(StockMovementLine)
class StockMovementLineAdmin(admin.ModelAdmin):
    list_display = ["id", "movement", "medicine", "batch", "quantity", "unit_cost", "total_cost", "created_at"]
    list_filter = ["tenant", "created_at"]
    search_fields = ["movement__movement_number", "medicine__english_name", "batch__batch_number"]
    raw_id_fields = ["tenant", "movement", "medicine", "batch", "source_location", "destination_location"]

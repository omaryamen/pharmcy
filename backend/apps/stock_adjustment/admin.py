"""Admin registrations for Enterprise Stock Adjustment & Stock Count module."""

from django.contrib import admin

from apps.stock_adjustment.models import (
    StockCount,
    StockCountHistory,
    StockCountLine,
    StockCountRecount,
    StockCountSession,
)


class StockCountLineInline(admin.TabularInline):
    model = StockCountLine
    extra = 0
    raw_id_fields = ["medicine", "batch", "storage_location"]


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = [
        "count_number",
        "tenant",
        "company",
        "warehouse",
        "count_type",
        "count_status",
        "is_blind_count",
        "freeze_inventory",
        "total_variance_cost",
        "created_at",
    ]
    list_filter = ["tenant", "count_type", "count_status", "is_blind_count", "freeze_inventory", "created_at"]
    search_fields = ["count_number", "reason", "notes"]
    raw_id_fields = [
        "tenant",
        "company",
        "branch",
        "warehouse",
        "storage_location",
        "created_by",
        "started_by",
        "completed_by",
        "approved_by",
        "reconciled_by",
    ]
    inlines = [StockCountLineInline]


@admin.register(StockCountLine)
class StockCountLineAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "stock_count",
        "medicine",
        "batch",
        "snapshot_quantity",
        "counted_quantity",
        "variance_quantity",
        "variance_direction",
        "created_at",
    ]
    list_filter = ["tenant", "variance_direction", "created_at"]
    search_fields = ["stock_count__count_number", "medicine__english_name", "batch__batch_number"]
    raw_id_fields = ["tenant", "stock_count", "medicine", "batch", "storage_location"]


@admin.register(StockCountSession)
class StockCountSessionAdmin(admin.ModelAdmin):
    list_display = ["session_number", "stock_count", "assigned_user", "warehouse", "session_status", "created_at"]
    list_filter = ["tenant", "session_status"]
    raw_id_fields = ["tenant", "stock_count", "assigned_user", "warehouse", "storage_location"]


@admin.register(StockCountRecount)
class StockCountRecountAdmin(admin.ModelAdmin):
    list_display = ["recount_number", "stock_count", "requested_by", "recounted_by", "recount_status", "created_at"]
    list_filter = ["tenant", "recount_status"]
    raw_id_fields = ["tenant", "stock_count", "stock_count_line", "requested_by", "recounted_by"]


@admin.register(StockCountHistory)
class StockCountHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "stock_count", "event_type", "performed_by", "timestamp"]
    list_filter = ["tenant", "event_type", "timestamp"]
    raw_id_fields = ["tenant", "stock_count", "performed_by"]

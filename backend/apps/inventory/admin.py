"""Django admin configuration for Inventory Domain."""

from __future__ import annotations

from django.contrib import admin

from apps.inventory.models import Batch, InventoryItem, InventoryTransaction


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ["batch_number", "medicine", "expiry_date", "status", "unit_cost", "selling_price", "tenant"]
    list_filter = ["status", "expiry_date", "tenant"]
    search_fields = ["batch_number", "lot_number", "medicine__name"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["medicine", "batch", "warehouse", "storage_location", "on_hand_quantity", "reserved_quantity", "status", "tenant"]
    list_filter = ["status", "warehouse", "tenant"]
    search_fields = ["medicine__name", "batch__batch_number", "warehouse__code", "storage_location__code"]


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_type", "quantity", "medicine", "batch", "warehouse", "reference_number", "created_at"]
    list_filter = ["transaction_type", "warehouse", "created_at"]
    search_fields = ["reference_number", "medicine__name", "batch__batch_number"]

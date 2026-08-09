"""Django admin configuration for Warehouse Domain."""

from __future__ import annotations

from django.contrib import admin

from apps.warehouses.models import StorageLocation, Warehouse


class StorageLocationInline(admin.TabularInline):
    model = StorageLocation
    extra = 0


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "warehouse_type", "status", "company", "branch", "manager", "tenant"]
    list_filter = ["status", "warehouse_type", "company", "tenant"]
    search_fields = ["code", "name", "arabic_name", "english_name", "city"]
    inlines = [StorageLocationInline]


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "location_type", "warehouse", "parent", "status"]
    list_filter = ["location_type", "status", "warehouse"]
    search_fields = ["code", "name", "arabic_name", "english_name"]

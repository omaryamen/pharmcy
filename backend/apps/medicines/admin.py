"""Django Admin configuration for Medicine Master Catalog."""

from __future__ import annotations

from django.contrib import admin

from apps.medicines.models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ["english_name", "arabic_name", "code", "sku", "barcode", "status", "dosage_form", "default_selling_price"]
    list_filter = ["status", "prescription_type", "medicine_type", "is_high_alert", "is_refrigerated"]
    search_fields = ["english_name", "arabic_name", "code", "sku", "barcode", "generic_name"]

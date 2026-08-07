"""Django Admin configuration for Enterprise Supplier Management."""

from __future__ import annotations

from django.contrib import admin

from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["display_name", "legal_name", "code", "supplier_type", "status", "country", "is_preferred", "is_blacklisted"]
    search_fields = ["display_name", "legal_name", "code", "email", "phone", "tax_number"]
    list_filter = ["status", "supplier_type", "risk_level", "is_preferred", "is_blacklisted"]

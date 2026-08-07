"""Django Admin configuration for Company Management."""

from __future__ import annotations

from django.contrib import admin

from apps.companies.models import Company, CompanySettings


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "code", "tenant", "business_type", "status", "country", "currency"]
    list_filter = ["business_type", "status", "country"]
    search_fields = ["legal_name", "commercial_name", "code", "tax_number", "tenant__name"]


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ["company", "tenant", "default_currency", "default_language", "updated_at"]
    search_fields = ["company__legal_name", "company__code"]

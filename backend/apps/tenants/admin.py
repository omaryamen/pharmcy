"""Django Admin configuration for Tenant Management."""

from __future__ import annotations

from django.contrib import admin

from apps.tenants.models import TenantDomain, TenantProfile, TenantSettings, TenantSubscription


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "display_name", "business_type", "country", "currency"]
    search_fields = ["legal_name", "tax_number", "registration_number"]


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ["tenant", "updated_at"]


@admin.register(TenantSubscription)
class TenantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["tenant", "plan", "billing_cycle", "status", "end_date", "is_trial"]
    list_filter = ["plan", "billing_cycle", "status", "is_trial"]
    search_fields = ["tenant__name", "tenant__slug"]


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ["domain_name", "tenant", "domain_type", "is_verified", "ssl_status", "is_primary"]
    list_filter = ["domain_type", "is_verified", "ssl_status", "is_primary"]
    search_fields = ["domain_name", "tenant__name"]

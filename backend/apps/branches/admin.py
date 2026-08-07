"""Django Admin configuration for Branch Management."""

from __future__ import annotations

from django.contrib import admin

from apps.branches.models import Branch, BranchSettings


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "company", "tenant", "branch_type", "status", "city", "manager"]
    list_filter = ["branch_type", "status", "city"]
    search_fields = ["name", "display_name", "code", "company__legal_name", "tenant__name"]


@admin.register(BranchSettings)
class BranchSettingsAdmin(admin.ModelAdmin):
    list_display = ["branch", "company", "tenant", "updated_at"]
    search_fields = ["branch__name", "branch__code", "company__legal_name"]

"""Django admin for core models."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Tenant, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-created_at",)
    list_display = (
        "email",
        "full_name",
        "phone",
        "status",
        "is_active",
        "email_verified",
        "phone_verified",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    list_filter = (
        "status",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "phone_verified",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identity", {"fields": ("username", "first_name", "last_name", "phone", "avatar")}),
        ("Preferences", {"fields": ("language", "timezone")}),
        (
            "Account state",
            {
                "fields": (
                    "status",
                    "email_verified",
                    "phone_verified",
                    "failed_login_attempts",
                    "password_changed_at",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions", "tenants")},
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )
    readonly_fields = (
        "failed_login_attempts",
        "password_changed_at",
        "last_login",
        "created_at",
        "updated_at",
        "deleted_at",
        "created_by",
        "updated_by",
    )
    filter_horizontal = ("groups", "user_permissions", "tenants")


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "slug", "status", "timezone", "locale", "is_active")
    search_fields = ("name", "code", "slug")
    list_filter = ("status", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")

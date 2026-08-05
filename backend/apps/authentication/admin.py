"""Django admin for authentication models."""

from __future__ import annotations

from django.contrib import admin

from .models import LoginSession, PasswordHistory, SecurityEvent, VerificationToken


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "device_name",
        "device_type",
        "ip_address",
        "remember_me",
        "is_active",
        "last_used_at",
        "expires_at",
        "revoked_at",
    )
    search_fields = ("user__email", "device_name", "ip_address", "refresh_token_jti")
    list_filter = ("device_type", "remember_me", "is_active", "revoked_reason")
    readonly_fields = ("refresh_token_jti", "created_at", "updated_at")
    raw_id_fields = ("user", "revoked_by")


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "is_usable", "attempts", "max_attempts", "expires_at", "consumed_at")
    search_fields = ("user__email", "token_hash")
    list_filter = ("kind",)
    readonly_fields = ("token_hash", "created_at", "updated_at")
    raw_id_fields = ("user",)

    @admin.display(boolean=True, description="Usable")
    def is_usable(self, obj) -> bool:
        return obj.is_usable


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("password_hash", "created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "ip_address", "device_name", "created_at")
    search_fields = ("user__email", "event_type", "ip_address")
    list_filter = ("event_type",)
    readonly_fields = ("event_type", "ip_address", "user_agent", "device_name", "details", "created_at")
    raw_id_fields = ("user", "session")

    def has_add_permission(self, request) -> bool:
        return False

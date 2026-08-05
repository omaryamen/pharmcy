"""Django admin for the RBAC models."""

from __future__ import annotations

from django.contrib import admin

from .models import (
    Permission,
    Role,
    RoleAuditLog,
    RoleGroup,
    RoleGroupMembership,
    RoleHierarchy,
    RolePermission,
    RoleVersion,
    UserPermissionOverride,
    UserRoleAssignment,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module", "category", "action", "scope", "is_system", "is_active")
    list_filter = ("scope", "module", "is_system", "is_active")
    search_fields = ("code", "name", "module")
    ordering = ("module", "category", "code")

    def has_delete_permission(self, request, obj=None) -> bool:
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    autocomplete_fields = ("permission",)


class RoleHierarchyInline(admin.TabularInline):
    model = RoleHierarchy
    fk_name = "child_role"
    extra = 0


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "is_protected", "is_default", "is_active")
    list_filter = ("is_protected", "is_default", "is_active", "tenant")
    search_fields = ("name", "code", "tenant__name")
    inlines = [RolePermissionInline, RoleHierarchyInline]
    readonly_fields = ("is_protected",)

    def has_delete_permission(self, request, obj=None) -> bool:
        if obj is not None and obj.is_protected:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission", "allow")
    list_filter = ("allow",)
    search_fields = ("role__code", "permission__code")


@admin.register(RoleGroup)
class RoleGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "is_active")
    list_filter = ("is_active", "tenant")
    search_fields = ("name", "code")


@admin.register(RoleGroupMembership)
class RoleGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "role")


@admin.register(RoleHierarchy)
class RoleHierarchyAdmin(admin.ModelAdmin):
    list_display = ("child_role", "parent_role")


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "tenant", "is_primary", "is_active", "created_at")
    list_filter = ("is_primary", "is_active", "tenant")
    search_fields = ("user__email", "role__code", "role__name")


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("user", "permission", "allow", "tenant")
    list_filter = ("allow", "tenant")
    search_fields = ("user__email", "permission__code")


@admin.register(RoleVersion)
class RoleVersionAdmin(admin.ModelAdmin):
    list_display = ("role", "version", "reason", "created_at")
    search_fields = ("role__code",)


@admin.register(RoleAuditLog)
class RoleAuditLogAdmin(admin.ModelAdmin):
    list_display = ("role", "action", "actor", "created_at")
    list_filter = ("action",)
    search_fields = ("role__code",)

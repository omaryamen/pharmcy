"""Permissions for User Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageUsers(BasePermission):
    """Requires permission to create, update, or manage users."""

    message = "Permission to manage users is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "users.user.update", tenant) or PermissionEngine().has_permission(
            user, "users.user.manage", tenant
        )


class CanViewUsers(BasePermission):
    """Requires tenant membership or read access to users."""

    message = "Permission to view users is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "users.user.read", tenant)

"""Permissions for Enterprise Warehouse & Storage Location Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageWarehouses(BasePermission):
    """Requires permission to create, update, or delete warehouses."""

    message = "Permission to manage warehouses is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return (
            PermissionEngine().has_permission(user, "warehouses.create", tenant)
            or PermissionEngine().has_permission(user, "warehouses.update", tenant)
            or PermissionEngine().has_permission(user, "warehouses.warehouse.create", tenant)
            or PermissionEngine().has_permission(user, "warehouses.warehouse.update", tenant)
            or PermissionEngine().has_permission(user, "warehouses.warehouse.manage", tenant)
        )


class CanViewWarehouses(BasePermission):
    """Requires tenant membership or read access to warehouses."""

    message = "Permission to view warehouses is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "warehouses.read", tenant) or PermissionEngine().has_permission(
            user, "warehouses.warehouse.read", tenant
        )


class CanManageLocations(BasePermission):
    """Requires permission to create, update, move, or delete storage locations."""

    message = "Permission to manage storage locations is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return (
            PermissionEngine().has_permission(user, "warehouses.location.create", tenant)
            or PermissionEngine().has_permission(user, "warehouses.location.update", tenant)
            or PermissionEngine().has_permission(user, "warehouses.location.delete", tenant)
        )


class CanViewLocations(BasePermission):
    """Requires read access to storage locations."""

    message = "Permission to view storage locations is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "warehouses.location.read", tenant) or PermissionEngine().has_permission(
            user, "warehouses.read", tenant
        )

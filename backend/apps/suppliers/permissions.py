"""Permissions for Enterprise Supplier Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageSuppliers(BasePermission):
    """Requires permission to create, update, or manage suppliers."""

    message = "Permission to manage suppliers is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "suppliers.supplier.update", tenant) or PermissionEngine().has_permission(
            user, "suppliers.supplier.manage", tenant
        )


class CanViewSuppliers(BasePermission):
    """Requires tenant membership or read access to suppliers."""

    message = "Permission to view suppliers is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "suppliers.supplier.read", tenant)

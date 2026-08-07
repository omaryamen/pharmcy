"""Permissions for Enterprise Pharmaceutical Reference Data endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageReferences(BasePermission):
    """Requires permission to create, update, or manage reference data."""

    message = "Permission to manage reference data is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "references.reference.update", tenant) or PermissionEngine().has_permission(
            user, "references.reference.manage", tenant
        )


class CanViewReferences(BasePermission):
    """Requires tenant membership or read access to reference data."""

    message = "Permission to view reference data is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "references.reference.read", tenant)

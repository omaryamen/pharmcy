"""Permissions for Enterprise Medicine Master Data endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageMedicines(BasePermission):
    """Requires permission to create, update, or manage medicines."""

    message = "Permission to manage medicine master catalog is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "medicines.medicine.update", tenant) or PermissionEngine().has_permission(
            user, "medicines.medicine.manage", tenant
        )


class CanViewMedicines(BasePermission):
    """Requires tenant membership or read access to medicines."""

    message = "Permission to view medicine master catalog is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "medicines.medicine.read", tenant)

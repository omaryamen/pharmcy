"""Permissions for Company Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageCompany(BasePermission):
    """Requires permission to create, update, deactivate, or delete companies."""

    message = "Permission to manage companies is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "companies.company.update", tenant) or PermissionEngine().has_permission(
            user, "companies.company.manage", tenant
        )


class CanViewCompany(BasePermission):
    """Requires tenant membership or read access to companies."""

    message = "Permission to view companies is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "companies.company.read", tenant)

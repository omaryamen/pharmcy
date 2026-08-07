"""Permissions for Branch Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageBranch(BasePermission):
    """Requires permission to create, update, or delete branches."""

    message = "Permission to manage branches is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "branches.branch.update", tenant) or PermissionEngine().has_permission(
            user, "branches.branch.manage", tenant
        )


class CanViewBranch(BasePermission):
    """Requires tenant membership or read access to branches."""

    message = "Permission to view branches is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "branches.branch.read", tenant)

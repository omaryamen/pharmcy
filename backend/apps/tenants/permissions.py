"""Permissions for Tenant Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class IsPlatformAdmin(BasePermission):
    """Platform Superuser or Staff Administrator."""

    message = "Platform administrator privileges are required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff))


class IsTenantOwner(BasePermission):
    """The user must be the designated owner of the current request tenant."""

    message = "Tenant owner access required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not tenant:
            return False
        return tenant.owner_id == user.pk


class CanManageTenantSettings(BasePermission):
    """Requires tenant settings management permission or tenant owner role."""

    message = "Permission to manage tenant settings is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "tenants.settings.update", tenant)


class CanManageTenantSubscription(BasePermission):
    """Requires tenant subscription management permission or tenant owner role."""

    message = "Permission to manage tenant subscription is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "tenants.subscription.update", tenant)

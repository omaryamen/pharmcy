"""Permissions for Enterprise Customer Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanManageCustomers(BasePermission):
    """Requires permission to create, update, or delete customers."""

    message = "Permission to manage customers is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return (
            PermissionEngine().has_permission(user, "customers.create", tenant)
            or PermissionEngine().has_permission(user, "customers.update", tenant)
            or PermissionEngine().has_permission(user, "customers.customer.update", tenant)
            or PermissionEngine().has_permission(user, "customers.customer.manage", tenant)
        )


class CanViewCustomers(BasePermission):
    """Requires tenant membership or read access to customers."""

    message = "Permission to view customers is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "customers.read", tenant) or PermissionEngine().has_permission(
            user, "customers.customer.read", tenant
        )


class CanViewCustomerMedicalProfile(BasePermission):
    """Requires explicit authorization to access sensitive medical profiles."""

    message = "Permission to access customer medical profiles is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "customers.medical_profile.read", tenant)


class CanManageCustomerMedicalProfile(BasePermission):
    """Requires explicit authorization to modify customer medical profiles."""

    message = "Permission to update customer medical profiles is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "customers.medical_profile.update", tenant)

"""Permissions for Enterprise Inventory & Batch Management endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


class CanViewInventory(BasePermission):
    """Requires read permission for inventory items."""

    message = "Permission to view inventory is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "inventory.read", tenant)


class CanManageInventory(BasePermission):
    """Requires permission to create or update inventory stock items."""

    message = "Permission to manage inventory items is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return (
            PermissionEngine().has_permission(user, "inventory.create", tenant)
            or PermissionEngine().has_permission(user, "inventory.update", tenant)
            or PermissionEngine().has_permission(user, "inventory.adjust", tenant)
        )


class CanAdjustInventory(BasePermission):
    """Requires permission to execute stock adjustments and quantity mutations."""

    message = "Permission to adjust stock quantities is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return PermissionEngine().has_permission(user, "inventory.adjust", tenant)


class CanViewBatches(BasePermission):
    """Requires read permission for pharmaceutical batches."""

    message = "Permission to view batch records is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "inventory.batch.read", tenant) or PermissionEngine().has_permission(
            user, "inventory.read", tenant
        )


class CanManageBatches(BasePermission):
    """Requires permission to create, update, block, or recall batches."""

    message = "Permission to manage batch records is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and tenant.owner_id == user.pk):
            return True
        return (
            PermissionEngine().has_permission(user, "inventory.batch.create", tenant)
            or PermissionEngine().has_permission(user, "inventory.batch.update", tenant)
            or PermissionEngine().has_permission(user, "inventory.batch.block", tenant)
            or PermissionEngine().has_permission(user, "inventory.batch.recall", tenant)
        )


class CanViewTransactions(BasePermission):
    """Requires permission to view inventory transaction logs."""

    message = "Permission to view inventory transaction history is required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (tenant and user.tenants.filter(pk=tenant.pk).exists()):
            return True
        return PermissionEngine().has_permission(user, "inventory.transaction.read", tenant) or PermissionEngine().has_permission(
            user, "inventory.read", tenant
        )

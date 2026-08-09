"""RBAC permission classes for Enterprise Stock Movement Engine endpoints."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.rbac.engine import PermissionEngine


def _check_permission(request, code: str) -> bool:
    user = getattr(request, "user", None)
    tenant = getattr(request, "tenant", None)
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return PermissionEngine().has_permission(user, code, tenant)


class CanViewStockMovements(BasePermission):
    message = "Permission to view stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.read")


class CanCreateStockMovements(BasePermission):
    message = "Permission to create stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.create")


class CanProcessStockMovements(BasePermission):
    message = "Permission to process stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.process")


class CanApproveStockMovements(BasePermission):
    message = "Permission to approve stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.approve")


class CanCancelStockMovements(BasePermission):
    message = "Permission to cancel stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.cancel")


class CanReverseStockMovements(BasePermission):
    message = "Permission to reverse stock movements is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.reverse")


class CanReceiveStock(BasePermission):
    message = "Permission to receive stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.receive")


class CanIssueStock(BasePermission):
    message = "Permission to issue stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.issue")


class CanTransferStock(BasePermission):
    message = "Permission to transfer stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.transfer")


class CanAdjustStock(BasePermission):
    message = "Permission to adjust stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.adjust")


class CanQuarantineStock(BasePermission):
    message = "Permission to quarantine stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.quarantine")


class CanReserveStock(BasePermission):
    message = "Permission to reserve stock is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.reserve")


class CanViewStockCosts(BasePermission):
    message = "Permission to view stock costs is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.cost.read")


class CanViewStockTraceability(BasePermission):
    message = "Permission to view stock traceability is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_movement.trace.read")

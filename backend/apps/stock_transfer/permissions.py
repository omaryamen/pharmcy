"""RBAC permission classes for Enterprise Stock Transfer module."""

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


class CanViewStockTransfers(BasePermission):
    message = "Permission to view stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.read")


class CanCreateStockTransfers(BasePermission):
    message = "Permission to create stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.create")


class CanRequestStockTransfers(BasePermission):
    message = "Permission to request stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.request")


class CanApproveStockTransfers(BasePermission):
    message = "Permission to approve stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.approve")


class CanPickStockTransfers(BasePermission):
    message = "Permission to pick stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.pick")


class CanDispatchStockTransfers(BasePermission):
    message = "Permission to dispatch stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.dispatch")


class CanReceiveStockTransfers(BasePermission):
    message = "Permission to receive stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.receive")


class CanRejectStockTransfers(BasePermission):
    message = "Permission to reject stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.reject")


class CanCancelStockTransfers(BasePermission):
    message = "Permission to cancel stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.cancel")


class CanReconcileStockTransfers(BasePermission):
    message = "Permission to reconcile stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.reconcile")


class CanReverseStockTransfers(BasePermission):
    message = "Permission to reverse stock transfers is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.reverse")


class CanViewTransferDiscrepancies(BasePermission):
    message = "Permission to view transfer discrepancies is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.discrepancy_view")


class CanResolveTransferDiscrepancies(BasePermission):
    message = "Permission to resolve transfer discrepancies is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_transfer.discrepancy_resolve")

"""RBAC permission classes for Enterprise Stock Adjustment & Stock Count module."""

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


class CanViewStockCounts(BasePermission):
    message = "Permission to view stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.read")


class CanCreateStockCounts(BasePermission):
    message = "Permission to create stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.create")


class CanStartStockCounts(BasePermission):
    message = "Permission to start stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.start")


class CanPerformStockCounts(BasePermission):
    message = "Permission to perform physical counting is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.perform")


class CanSubmitStockCounts(BasePermission):
    message = "Permission to submit stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.submit")


class CanReviewStockCounts(BasePermission):
    message = "Permission to review stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.review")


class CanApproveStockCounts(BasePermission):
    message = "Permission to approve stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.approve")


class CanReconcileStockCounts(BasePermission):
    message = "Permission to reconcile stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.reconcile")


class CanCancelStockCounts(BasePermission):
    message = "Permission to cancel stock counts is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.cancel")


class CanRequestRecount(BasePermission):
    message = "Permission to request recount is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.recount")


class CanViewSystemQuantity(BasePermission):
    message = "Permission to view system snapshot quantity is required."

    def has_permission(self, request, view) -> bool:
        return _check_permission(request, "stock_adjustment.view_system_quantity")

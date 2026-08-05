"""Custom DRF permissions used across the API."""

from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActive(BasePermission):
    """Authenticated, active and not soft-deleted (deleted accounts can no
    longer use their previously issued tokens)."""

    message = "Authentication credentials were not provided or the account is inactive."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if user is None or not user.is_authenticated:
            return False
        if getattr(user, "is_deleted", False):
            return False
        return bool(user.is_active)


class IsSuperUser(BasePermission):
    """Superuser only (platform admin endpoints)."""

    message = "Administrator privileges are required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user is not None and request.user.is_superuser)


class HasTenantContext(BasePermission):
    """The request must carry a resolvable tenant header."""

    message = "A valid X-Tenant-ID header is required."

    def has_permission(self, request, view) -> bool:
        return getattr(request, "tenant", None) is not None


class IsTenantMember(BasePermission):
    """The authenticated user must be a member of the request's tenant.

    Superusers bypass the membership check (platform support).
    """

    message = "User does not have access to this tenant."

    def has_permission(self, request, view) -> bool:
        if request.user is None or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return False
        return request.user.tenants.filter(pk=tenant.pk).exists()


class IsReadOnly(BasePermission):
    """Allow safe methods only (GET/HEAD/OPTIONS)."""

    def has_permission(self, request, view) -> bool:
        return request.method in {"GET", "HEAD", "OPTIONS"}

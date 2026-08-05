"""RBAC request helpers."""

from __future__ import annotations

from .engine import PermissionEngine


def effective_permissions_for(request) -> set[str]:
    """Effective permission codes for the current request (cached per request)."""
    return PermissionEngine().permissions_for_request(request)


def can(request, code: str) -> bool:
    """Whether the current request's actor holds ``code`` in the request tenant."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    tenant = getattr(request, "tenant", None)
    return PermissionEngine().has_permission(user, code, tenant)

"""Function-level authorization decorators.

Prefer the DRF permission classes (``HasPermission`` …) for viewsets. These
decorators are for plain function views, Celery tasks and service entry
points where a full DRF permission object is not available.
"""

from __future__ import annotations

from functools import wraps

from apps.common.exceptions import PermissionDeniedError
from apps.common.utils.context import get_current_tenant, get_current_user

from .engine import PermissionEngine


def require_permission(code: str):
    """Deny the call unless the current user holds ``code``."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None) if request is not None else get_current_user()
            if user is None or not getattr(user, "is_authenticated", False):
                raise PermissionDeniedError("Authentication required.")
            tenant = getattr(request, "tenant", None) if request is not None else get_current_tenant()
            if not PermissionEngine().has_permission(user, code, tenant):
                raise PermissionDeniedError(f"Permission '{code}' is required.")
            return fn(request, *args, **kwargs)

        return wrapper

    return decorator


def require_permissions(*codes: str, mode: str = "any"):
    """Require any (default) or all of the given codes.

    ``mode="all"`` requires every code; otherwise a single match suffices.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None) if request is not None else get_current_user()
            if user is None or not getattr(user, "is_authenticated", False):
                raise PermissionDeniedError("Authentication required.")
            tenant = getattr(request, "tenant", None) if request is not None else get_current_tenant()
            engine = PermissionEngine()
            ok = engine.has_all(user, list(codes), tenant) if mode == "all" else engine.has_any(user, list(codes), tenant)
            if not ok:
                raise PermissionDeniedError("You do not have the required permissions.")
            return fn(request, *args, **kwargs)

        return wrapper

    return decorator

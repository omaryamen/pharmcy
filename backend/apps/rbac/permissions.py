"""DRF authorization layer for RBAC.

Wire a view/viewset to the engine with:

- ``permission_classes = [HasPermission]`` and a ``permission_code_prefix``
  (e.g. ``"inventory.stock"`` → ``inventory.stock.read`` for GET, ``.create``
  for POST, ``.update`` for PUT/PATCH, ``.delete`` for DELETE); or
- an explicit ``required_permissions`` mapping::

      required_permissions = {
          "list": "inventory.stock.read",
          "retrieve": "inventory.stock.read",
          "create": "inventory.stock.create",
          "update": "inventory.stock.update",
          "destroy": "inventory.stock.delete",
      }

Superusers bypass all checks when ``RBAC_SUPERADMIN_BYPASS`` is enabled.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import BasePermission

from apps.common.exceptions import PermissionDeniedError

from .engine import PermissionEngine

#: HTTP method → CRUD action used when deriving codes from a prefix.
_ACTION_BY_METHOD = {
    "get": "read",
    "head": "read",
    "options": "read",
    "post": "create",
    "put": "update",
    "patch": "update",
    "delete": "delete",
}


def resolve_permission_codes(view, request) -> list[str]:
    """Resolve the permission codes the view declares for this request."""
    mapping = getattr(view, "required_permissions", None)
    if mapping:
        action = getattr(view, "action", None) or request.method.lower()
        code = mapping.get(action)
        if code:
            return [code]

    prefix = getattr(view, "permission_code_prefix", None)
    if prefix:
        action = _ACTION_BY_METHOD.get(request.method.lower(), "manage")
        return [f"{prefix}.{action}"]

    explicit = getattr(view, "permission_code", None)
    if explicit:
        return [explicit]

    return []


def _is_authorized_actor(user) -> bool:
    return (
        user is not None
        and getattr(user, "is_authenticated", False)
        and not getattr(user, "is_deleted", False)
        and bool(user.is_active)
    )


def _superuser_bypass(user) -> bool:
    return getattr(user, "is_superuser", False) and settings.RBAC_SUPERADMIN_BYPASS


class HasPermission(BasePermission):
    """The user needs the resolved permission code for the request."""

    message = "You do not have permission to perform this action."
    permission_code = None

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not _is_authorized_actor(user):
            return False
        if _superuser_bypass(user):
            return True
        codes = resolve_permission_codes(view, request)
        if not codes:
            return False
        engine = PermissionEngine()
        tenant = getattr(request, "tenant", None)
        return any(engine.has_permission(user, code, tenant) for code in codes)


class HasAnyPermission(BasePermission):
    """The user needs at least one of ``permissions``."""

    message = "You do not have permission to perform this action."
    permissions: list[str] = []

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not _is_authorized_actor(user):
            return False
        if _superuser_bypass(user):
            return True
        engine = PermissionEngine()
        tenant = getattr(request, "tenant", None)
        return any(engine.has_permission(user, code, tenant) for code in self.permissions)


class HasAllPermissions(BasePermission):
    """The user needs every code in ``permissions``."""

    message = "You do not have permission to perform this action."
    permissions: list[str] = []

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not _is_authorized_actor(user):
            return False
        if _superuser_bypass(user):
            return True
        engine = PermissionEngine()
        tenant = getattr(request, "tenant", None)
        return all(engine.has_permission(user, code, tenant) for code in self.permissions)


class HasModuleAccess(BasePermission):
    """The user needs any permission belonging to a module.

    Declare ``module = "inventory"`` on the view.
    """

    message = "You do not have access to this module."
    module: str | None = None

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not _is_authorized_actor(user):
            return False
        if _superuser_bypass(user):
            return True
        module = getattr(view, "module", None) or self.module
        if not module:
            return False
        engine = PermissionEngine()
        return engine.has_module_access(user, module, getattr(request, "tenant", None))


class HasObjectPermission(BasePermission):
    """Like ``HasPermission`` but also enforced per-object.

    The object must belong to the request tenant (when it exposes
    ``tenant_id``) and the actor must hold the action permission.
    """

    message = "You do not have permission to perform this action on this resource."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not _is_authorized_actor(user):
            return False
        if _superuser_bypass(user):
            return True
        codes = resolve_permission_codes(view, request)
        if not codes:
            return False
        engine = PermissionEngine()
        tenant = getattr(request, "tenant", None)
        return any(engine.has_permission(user, code, tenant) for code in codes)

    def has_object_permission(self, request, view, obj) -> bool:
        tenant = getattr(request, "tenant", None)
        if tenant is not None and getattr(obj, "tenant_id", None) is not None and obj.tenant_id != tenant.pk:
            return False
        user = request.user
        if _superuser_bypass(user):
            return True
        codes = resolve_permission_codes(view, request)
        engine = PermissionEngine()
        return any(engine.has_permission(user, code, tenant) for code in codes)


def raise_permission_denied(code: str) -> None:
    """Raise the domain 403 error for a missing permission."""
    raise PermissionDeniedError(f"Permission '{code}' is required.")

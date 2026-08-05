"""The permission engine.

`PermissionEngine` is the single place business code asks "can this user do X
in this tenant?". It resolves the effective permission set once per
(user, tenant) pair, caches it, and answers point checks with no further I/O.

Precedence (highest wins):

1. user-level override (``UserPermissionOverride``) for the code;
2. a direct role-permission link on any assigned role (source ``direct``);
3. an inherited link (source ``inherited``) through role parents;
4. across different roles assigned to the same user, a grant beats a denial
   (union semantics).

Superusers bypass the engine entirely when ``RBAC_SUPERADMIN_BYPASS`` is on.
"""

from __future__ import annotations

from django.conf import settings

from apps.common.utils.context import get_current_tenant

from ..models import Permission, UserPermissionOverride, UserRoleAssignment
from .cache import PermissionCache
from .resolver import PermissionResolver


class PermissionEngine:
    def __init__(self, cache_backend=None, resolver: PermissionResolver | None = None) -> None:
        self.cache = PermissionCache(cache_backend) if cache_backend is not None else PermissionCache()
        self.resolver = resolver or PermissionResolver()

    # ------------------------------------------------------------------
    # Effective permission resolution
    # ------------------------------------------------------------------
    def effective_permissions(self, user, tenant=None, *, use_cache: bool = True) -> set[str]:
        """The exact set of granted permission codes for ``user`` in ``tenant``."""
        if user is None or getattr(user, "is_authenticated", False) is False:
            return set()
        if getattr(user, "is_superuser", False) and settings.RBAC_SUPERADMIN_BYPASS:
            return set(Permission.objects.filter(is_active=True).values_list("code", flat=True))
        if tenant is None:
            tenant = get_current_tenant()
        if tenant is None:
            return set()

        if use_cache:
            cached = self.cache.get_effective(user.pk, tenant.pk)
            if cached is not None:
                return cached
        codes = self._compute(user, tenant)
        if use_cache:
            self.cache.set_effective(user.pk, tenant.pk, codes)
        return codes

    def _compute(self, user, tenant) -> set[str]:
        overrides = {
            override.permission.code: override.allow
            for override in UserPermissionOverride.objects.filter(
                user=user, tenant=tenant, permission__is_active=True
            ).select_related("permission")
        }
        assignments = UserRoleAssignment.objects.filter(
            user=user, tenant=tenant, is_active=True, role__is_active=True
        ).select_related("role")

        allowed: set[str] = set()
        denied: set[str] = set()
        for assignment in assignments:
            for code, (allow, _source) in self.resolver.role_permission_map(assignment.role).items():
                if code in overrides:
                    continue
                if allow:
                    denied.discard(code)
                    allowed.add(code)
                elif code not in allowed:
                    denied.add(code)

        for code, allow in overrides.items():
            if allow:
                denied.discard(code)
                allowed.add(code)
            else:
                allowed.discard(code)
                denied.add(code)

        return allowed - denied

    # ------------------------------------------------------------------
    # Point checks
    # ------------------------------------------------------------------
    def has_permission(self, user, code: str, tenant=None) -> bool:
        if user is None or getattr(user, "is_authenticated", False) is False:
            return False
        if getattr(user, "is_superuser", False) and settings.RBAC_SUPERADMIN_BYPASS:
            return True
        return code in self.effective_permissions(user, tenant)

    def has_any(self, user, codes: list[str], tenant=None) -> bool:
        return any(self.has_permission(user, code, tenant) for code in codes)

    def has_all(self, user, codes: list[str], tenant=None) -> bool:
        return all(self.has_permission(user, code, tenant) for code in codes)

    def modules_for(self, user, tenant=None) -> set[str]:
        codes = self.effective_permissions(user, tenant)
        return {code.split(".")[0] for code in codes}

    def has_module_access(self, user, module: str, tenant=None) -> bool:
        if getattr(user, "is_superuser", False) and settings.RBAC_SUPERADMIN_BYPASS:
            return True
        return any(code.startswith(f"{module}.") for code in self.effective_permissions(user, tenant))

    # ------------------------------------------------------------------
    # Request-scoped helper (shared by middleware + permission classes)
    # ------------------------------------------------------------------
    def permissions_for_request(self, request) -> set[str]:
        """Effective codes for the current request, computed once per request."""
        user = getattr(request, "user", None)
        cached = getattr(request, "_rbac_effective", None)
        if cached is not None and cached.get("user_id") == getattr(user, "pk", None):
            return cached["codes"]
        tenant = getattr(request, "tenant", None)
        codes = self.effective_permissions(user, tenant)
        request._rbac_effective = {"user_id": getattr(user, "pk", None), "codes": codes}
        return codes

"""RBAC model signals.

- Tenant bootstrap: when a new tenant is created, provision the baseline
  ``admin`` and ``member`` roles (idempotent).
- Cache invalidation: any mutation of the RBAC graph bumps the global cache
  version so every previously computed effective-permission set is stale.
"""

from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.models import Tenant

from .engine import PermissionCache
from .models import (
    Permission,
    Role,
    RoleGroupMembership,
    RoleHierarchy,
    RolePermission,
    UserPermissionOverride,
    UserRoleAssignment,
)

_GRAPH_MODELS = (
    Permission,
    Role,
    RolePermission,
    RoleGroupMembership,
    RoleHierarchy,
    UserRoleAssignment,
    UserPermissionOverride,
)


def _invalidate(sender, instance, **kwargs) -> None:
    PermissionCache().invalidate()


for _model in _GRAPH_MODELS:
    post_save.connect(_invalidate, sender=_model, dispatch_uid=f"rbac_invalidate_{_model._meta.label_lower}_save")
    post_delete.connect(_invalidate, sender=_model, dispatch_uid=f"rbac_invalidate_{_model._meta.label_lower}_delete")


@receiver(post_save, sender=Tenant, dispatch_uid="rbac_bootstrap_tenant")
def bootstrap_tenant(sender, instance, created, **kwargs) -> None:
    """Create baseline roles when a tenant is provisioned."""
    if not created:
        return
    if not settings.RBAC_BOOTSTRAP_ON_TENANT_CREATE:
        return
    from .services import RoleBootstrapService

    RoleBootstrapService().ensure_tenant_defaults(instance)

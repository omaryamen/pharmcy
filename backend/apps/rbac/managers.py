"""QuerySet / Manager classes combining tenant scoping and soft deletion.

``TenantAwareModel`` installs ``TenantManager`` and ``SoftDeleteBase``
installs ``SoftDeleteManager``; a model inheriting both must pick an explicit
manager. ``TenantSoftDeleteManager`` hides soft-deleted rows *and* provides
tenant-scoped helpers.
"""

from __future__ import annotations

from django.db import models

from apps.common.models.managers import SoftDeleteQuerySet, TenantQuerySet


class TenantSoftDeleteQuerySet(TenantQuerySet, SoftDeleteQuerySet):
    """Tenant-scoped queryset that understands soft deletion semantics."""


class TenantSoftDeleteManager(models.Manager):
    """Default manager: tenant helpers on top of the soft-delete filter."""

    def get_queryset(self) -> TenantSoftDeleteQuerySet:
        return TenantSoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self) -> TenantSoftDeleteQuerySet:
        return TenantSoftDeleteQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)

    def active(self):
        return self.get_queryset().active()

"""QuerySet and Manager base classes for soft-delete and tenant scoping."""

from __future__ import annotations

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    """QuerySet that understands soft-deletion semantics."""

    def delete(self) -> int:
        """Soft-delete all rows in this queryset (bulk update)."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Permanently remove all rows in this queryset."""
        return super().delete()

    def alive(self) -> QuerySet:
        return self.filter(is_deleted=False)

    def deleted(self) -> QuerySet:
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Default manager: hides soft-deleted rows."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)


class AllObjectsManager(models.Manager):
    """Manager that includes soft-deleted rows."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)


class TenantQuerySet(QuerySet):
    """QuerySet with tenant-scoping helpers."""

    def for_tenant(self, tenant) -> QuerySet:
        if tenant is None:
            return self.none()
        return self.filter(tenant=tenant)

    def active(self) -> QuerySet:
        return self.filter(is_active=True)


class TenantManager(models.Manager):
    """Manager returning a TenantQuerySet."""

    def get_queryset(self) -> TenantQuerySet:
        return TenantQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant) -> QuerySet:
        return self.get_queryset().for_tenant(tenant)

    def active(self) -> QuerySet:
        return self.get_queryset().active()

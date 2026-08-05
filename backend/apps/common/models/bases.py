"""Abstract base models: UUID PK, timestamps, soft delete, audit.

Compose the pieces you need, e.g.::

    class StockItem(FullAuditModel, TenantAwareModel): ...

MRO note: ``FullAuditModel`` already inherits ``BaseModel``
(UUID + timestamps + soft delete) and adds audit fields.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.utils.context import get_current_user

from .managers import AllObjectsManager, SoftDeleteManager


class UUIDBase(models.Model):
    """UUID primary key for all domain entities."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")

    class Meta:
        abstract = True


class TimeStampedBase(models.Model):
    """Automatic creation / update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        abstract = True


class SoftDeleteBase(models.Model):
    """Logical deletion: rows are flagged, never physically removed by default."""

    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name="Is deleted")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted at")

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents: bool = False) -> None:
        """Soft-delete this instance."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Permanently remove this instance from the database."""
        return super().delete(using=using, keep_parents=keep_parents)

    @property
    def is_soft_deleted(self) -> bool:
        return self.is_deleted


class AuditBase(models.Model):
    """Who created / last updated a record, captured from request context."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Created by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Updated by",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        user = get_current_user()
        if user is not None and user.is_authenticated:
            if self._state.adding:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)


class UUIDTimeStampedModel(UUIDBase, TimeStampedBase):
    """UUID PK + timestamps (no soft delete)."""

    class Meta:
        abstract = True


class BaseModel(UUIDTimeStampedModel, SoftDeleteBase):
    """UUID PK + timestamps + soft delete (no audit)."""

    class Meta:
        abstract = True


class FullAuditModel(BaseModel, AuditBase):
    """The recommended base for business entities: UUID + timestamps +
    soft delete + created_by/updated_by audit."""

    class Meta:
        abstract = True

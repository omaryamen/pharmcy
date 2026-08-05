"""Base repository: a thin, typed data-access layer over Django ORM.

Repositories isolate persistence concerns. Business logic must live in
services; services talk to repositories; viewsets talk to services.
Subclasses declare ``model`` and may add domain-specific queries.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, TypeVar

from django.db import models

T = TypeVar("T", bound=models.Model)


class BaseRepository(Generic[T]):
    model: type[T] = None  # override in subclasses

    def __init__(self, model: type[T] | None = None) -> None:
        if model is not None:
            self.model = model
        if self.model is None:
            raise ValueError("BaseRepository requires a model.")

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------
    def get_queryset(self) -> models.QuerySet[T]:
        return self.model.objects.all()

    def all(self) -> models.QuerySet[T]:
        return self.get_queryset()

    def get(self, **kwargs) -> T:
        return self.get_queryset().get(**kwargs)

    def get_or_none(self, **kwargs) -> T | None:
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def filter(self, *args, **kwargs) -> models.QuerySet[T]:
        return self.get_queryset().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs) -> models.QuerySet[T]:
        return self.get_queryset().exclude(*args, **kwargs)

    def first(self) -> T | None:
        return self.get_queryset().first()

    def exists(self, **kwargs) -> bool:
        return self.get_queryset().filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        return self.get_queryset().filter(**kwargs).count()

    def get_or_create(self, defaults: dict | None = None, **kwargs) -> tuple[T, bool]:
        return self.get_queryset().get_or_create(defaults=defaults, **kwargs)

    def update_or_create(self, defaults: dict | None = None, **kwargs) -> tuple[T, bool]:
        return self.get_queryset().update_or_create(defaults=defaults, **kwargs)

    def select_for_update(self, queryset: models.QuerySet[T] | None = None) -> models.QuerySet[T]:
        return (queryset or self.get_queryset()).select_for_update()

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create(self, **kwargs) -> T:
        return self.get_queryset().create(**kwargs)

    def bulk_create(
        self, instances: Iterable[T], batch_size: int | None = None, ignore_conflicts: bool = False
    ) -> list[T]:
        return self.get_queryset().bulk_create(
            list(instances),
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
        )

    def save(self, instance: T, **kwargs) -> T:
        instance.save(**kwargs)
        return instance

    def update(self, instance: T, **fields) -> T:
        """Apply field updates to an instance and persist them."""
        for field, value in fields.items():
            setattr(instance, field, value)
        instance.save(update_fields=[*fields.keys(), "updated_at"])
        return instance

    def delete(self, instance: T) -> T:
        """Delete an instance. Models with ``SoftDeleteBase`` soft-delete;
        other models are removed permanently."""
        instance.delete()
        return instance

    def hard_delete(self, instance: T) -> T:
        """Permanently remove an instance regardless of soft-delete support."""
        delete_method = getattr(instance, "hard_delete", None)
        if delete_method is not None:
            delete_method()
        else:
            self.model.objects.filter(pk=instance.pk).delete()
        return instance

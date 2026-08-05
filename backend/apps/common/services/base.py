"""Base service: the unit of business logic.

Services own business rules and transactions; they delegate persistence to
a repository. All state-changing operations run inside ``transaction.atomic``
so a failure never leaves partial writes.

Subclasses set ``model`` (and optionally ``repository_class``) and override
``validate_*`` hooks for business validation.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from django.db import models, transaction

from apps.common.exceptions import NotFoundError
from apps.common.repositories.base import BaseRepository
from apps.common.utils.context import get_current_tenant

T = TypeVar("T", bound=models.Model)


class BaseService(Generic[T]):
    model: type[T] = None  # override in subclasses
    repository_class: type[BaseRepository] = BaseRepository

    def __init__(self, repository: BaseRepository | None = None) -> None:
        if repository is not None:
            self.repository = repository
        else:
            self.repository = self.repository_class(self.model)
        if self.model is None:
            self.model = self.repository.model

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get(self, id, *, include_deleted: bool = False) -> T:
        queryset = self.repository.all()
        if include_deleted and hasattr(self.repository.model, "all_objects"):
            queryset = self.repository.model.all_objects.all()
        try:
            return queryset.get(pk=id)
        except self.model.DoesNotExist as exc:
            raise NotFoundError(f"{self.model.__name__} not found.") from exc

    def get_or_none(self, **kwargs):
        return self.repository.get_or_none(**kwargs)

    def list(self, **filters) -> models.QuerySet[T]:
        queryset = self.repository.filter(**filters)
        tenant = get_current_tenant()
        if tenant is not None and hasattr(self.model, "tenant"):
            queryset = queryset.filter(tenant=tenant)
        return queryset

    def exists(self, **kwargs) -> bool:
        return self.repository.exists(**kwargs)

    def count(self, **kwargs) -> int:
        return self.repository.count(**kwargs)

    # ------------------------------------------------------------------
    # Writes (transactional)
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, data: dict) -> T:
        self.validate_create(data)
        payload = dict(data)
        tenant = get_current_tenant()
        if tenant is not None and hasattr(self.model, "tenant") and "tenant" not in payload:
            payload["tenant"] = tenant
        return self.repository.create(**payload)

    @transaction.atomic
    def update(self, id, data: dict) -> T:
        instance = self.get(id)
        self.validate_update(data)
        return self.repository.update(instance, **data)

    @transaction.atomic
    def delete(self, id) -> T:
        instance = self.get(id)
        self.validate_delete(instance)
        return self.repository.delete(instance)

    @transaction.atomic
    def hard_delete(self, id) -> T:
        instance = self.get(id, include_deleted=True)
        self.validate_delete(instance)
        return self.repository.hard_delete(instance)

    # ------------------------------------------------------------------
    # Validation hooks (override in subclasses)
    # ------------------------------------------------------------------
    def validate_create(self, data: dict) -> None:
        """Raise PharmaCloudError / ValidationFailedError on invalid data."""

    def validate_update(self, data: dict) -> None:
        """Raise PharmaCloudError / ValidationFailedError on invalid data."""

    def validate_delete(self, instance: T) -> None:
        """Raise PharmaCloudError if the instance must not be deleted."""

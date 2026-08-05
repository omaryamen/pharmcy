"""Repository + service layer tests."""

from __future__ import annotations

import pytest

from apps.common.exceptions import NotFoundError
from apps.common.repositories.base import BaseRepository
from apps.common.services.base import BaseService
from apps.core.models import Tenant


@pytest.mark.django_db
class TestBaseRepository:
    def test_crud_flow(self):
        repo = BaseRepository(Tenant)

        created = repo.create(name="Alpha", code="ALP1", slug="alpha")
        assert created.pk is not None
        assert repo.exists(pk=created.pk) is True
        assert repo.count() == 1

        fetched = repo.get(pk=created.pk)
        assert fetched.name == "Alpha"

        repo.update(fetched, name="Alpha Updated")
        assert repo.get(pk=created.pk).name == "Alpha Updated"

        repo.hard_delete(created)
        assert repo.get_or_none(pk=created.pk) is None

    def test_get_raises_does_not_exist(self):
        repo = BaseRepository(Tenant)
        with pytest.raises(Tenant.DoesNotExist):
            repo.get(pk="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
class TestBaseService:
    def test_create_update_hard_delete(self):
        service = BaseService(repository=BaseRepository(Tenant))

        instance = service.create({"name": "Beta", "code": "BET1", "slug": "beta"})
        assert instance.name == "Beta"

        updated = service.update(instance.pk, {"name": "Beta Updated"})
        assert updated.name == "Beta Updated"

        service.hard_delete(instance.pk)
        with pytest.raises(NotFoundError):
            service.get(instance.pk)

    def test_get_unknown_id_raises_not_found(self):
        service = BaseService(repository=BaseRepository(Tenant))
        with pytest.raises(NotFoundError):
            service.get("00000000-0000-0000-0000-000000000000")

    def test_list_returns_all(self, db):
        service = BaseService(repository=BaseRepository(Tenant))
        assert service.count() == 0

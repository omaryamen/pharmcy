"""Manufacturer Repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.references.models import Manufacturer


class ManufacturerRepository(BaseRepository[Manufacturer]):
    model = Manufacturer

    def get_by_code(self, tenant, code: str) -> Manufacturer | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

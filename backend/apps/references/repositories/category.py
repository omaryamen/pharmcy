"""Medicine Category Repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.references.models import MedicineCategory


class MedicineCategoryRepository(BaseRepository[MedicineCategory]):
    model = MedicineCategory

    def root_categories(self, tenant) -> list[MedicineCategory]:
        return list(self.filter(tenant=tenant, parent__isnull=True))

    def get_by_code(self, tenant, code: str) -> MedicineCategory | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

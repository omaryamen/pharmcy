"""Dosage Form Repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.references.models import DosageForm


class DosageFormRepository(BaseRepository[DosageForm]):
    model = DosageForm

    def get_by_code(self, tenant, code: str) -> DosageForm | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

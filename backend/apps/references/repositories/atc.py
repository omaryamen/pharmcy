"""ATC Classification Repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.references.models import AtcClassification


class AtcClassificationRepository(BaseRepository[AtcClassification]):
    model = AtcClassification

    def get_by_code(self, tenant, code: str) -> AtcClassification | None:
        return self.get_or_none(tenant=tenant, code=code.upper().strip())

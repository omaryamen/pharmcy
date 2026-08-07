"""Company Settings repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.companies.models import CompanySettings


class CompanySettingsRepository(BaseRepository[CompanySettings]):
    model = CompanySettings

    def get_for_company(self, company) -> CompanySettings | None:
        return self.get_or_none(company=company)

"""Company repository for database access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.companies.models import Company


class CompanyRepository(BaseRepository[Company]):
    model = Company

    def get_by_code(self, tenant, code: str) -> Company | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

    def get_by_slug(self, tenant, slug: str) -> Company | None:
        return self.get_or_none(tenant=tenant, slug=slug.lower().strip())

    def for_tenant(self, tenant) -> list[Company]:
        return list(self.filter(tenant=tenant))

    def get_with_settings(self, tenant, pk) -> Company | None:
        return self.get_queryset().select_related("settings", "tenant").filter(tenant=tenant, pk=pk).first()

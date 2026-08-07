"""Branch repository for DB access layer."""

from __future__ import annotations

from apps.branches.models import Branch
from apps.common.repositories.base import BaseRepository


class BranchRepository(BaseRepository[Branch]):
    model = Branch

    def get_by_code(self, company, code: str) -> Branch | None:
        return self.get_or_none(company=company, code=code.lower().strip())

    def get_by_slug(self, company, slug: str) -> Branch | None:
        return self.get_or_none(company=company, slug=slug.lower().strip())

    def for_company(self, company) -> list[Branch]:
        return list(self.filter(company=company))

    def for_tenant(self, tenant) -> list[Branch]:
        return list(self.filter(tenant=tenant))

    def get_with_relations(self, tenant, pk) -> Branch | None:
        return self.get_queryset().select_related("settings", "company", "tenant", "manager").filter(tenant=tenant, pk=pk).first()

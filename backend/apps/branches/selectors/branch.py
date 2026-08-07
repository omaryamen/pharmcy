"""Branch selector functions for tenant & company-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.branches.models import Branch
from apps.branches.repositories import BranchRepository


class BranchSelector:
    def __init__(self) -> None:
        self.repository = BranchRepository()

    def list_branches(
        self,
        tenant,
        *,
        company_id: str | None = None,
        status: str | None = None,
        branch_type: str | None = None,
        search: str | None = None,
    ) -> QuerySet[Branch]:
        qs = self.repository.filter(tenant=tenant).select_related("settings", "company", "tenant", "manager")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if status:
            qs = qs.filter(status=status)
        if branch_type:
            qs = qs.filter(branch_type=branch_type)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search) | qs.filter(display_name__icontains=search)
        return qs

    def get_branch_detail(self, tenant, branch_id) -> Branch | None:
        return self.repository.get_with_relations(tenant, branch_id)

    def get_branch_stats(self, branch: Branch) -> dict[str, Any]:
        return {
            "branch_id": str(branch.pk),
            "name": branch.name,
            "code": branch.code,
            "company_name": branch.company.legal_name,
            "status": branch.status,
            "branch_type": branch.branch_type,
            "active_pos_terminals": 0,
            "active_employees": 0,
            "inventory_item_count": 0,
        }

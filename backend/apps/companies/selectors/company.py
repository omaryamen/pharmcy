"""Company selector functions for tenant-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.companies.models import Company
from apps.companies.repositories import CompanyRepository


class CompanySelector:
    def __init__(self) -> None:
        self.repository = CompanyRepository()

    def list_companies(self, tenant, *, status: str | None = None, search: str | None = None) -> QuerySet[Company]:
        qs = self.repository.filter(tenant=tenant).select_related("settings", "tenant")
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(legal_name__icontains=search) | qs.filter(code__icontains=search) | qs.filter(commercial_name__icontains=search)
        return qs

    def get_company_detail(self, tenant, company_id) -> Company | None:
        return self.repository.get_with_settings(tenant, company_id)

    def get_company_stats(self, company: Company) -> dict[str, Any]:
        return {
            "company_id": str(company.pk),
            "legal_name": company.legal_name,
            "code": company.code,
            "status": company.status,
            "country": company.country,
            "currency": company.currency,
            "active_branches": 0,  # Placeholder unblocked until Branch module
            "active_employees": 0,
            "active_warehouses": 0,
        }

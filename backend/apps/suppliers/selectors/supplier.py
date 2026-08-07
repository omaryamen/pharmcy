"""Supplier selector functions for tenant & company-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from apps.suppliers.models import Supplier
from apps.suppliers.repositories import SupplierRepository


class SupplierSelector:
    def __init__(self) -> None:
        self.repository = SupplierRepository()

    def list_suppliers(
        self,
        tenant,
        *,
        company_id: str | None = None,
        supplier_type: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        is_preferred: bool | None = None,
        is_blacklisted: bool | None = None,
        search: str | None = None,
    ) -> QuerySet[Supplier]:
        qs = self.repository.filter(tenant=tenant).select_related("company", "tenant")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if supplier_type:
            qs = qs.filter(supplier_type=supplier_type)
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if status:
            qs = qs.filter(status=status)
        if is_preferred is not None:
            qs = qs.filter(is_preferred=is_preferred)
        if is_blacklisted is not None:
            qs = qs.filter(is_blacklisted=is_blacklisted)

        if search:
            qs = qs.filter(
                Q(display_name__icontains=search)
                | Q(legal_name__icontains=search)
                | Q(code__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(tax_number__icontains=search)
                | Q(commercial_registration__icontains=search)
            )

        return qs

    def get_supplier_detail(self, tenant, supplier_id) -> Supplier | None:
        return self.repository.get_or_none(tenant=tenant, pk=supplier_id)

    def get_supplier_stats(self, tenant) -> dict[str, Any]:
        total_suppliers = self.repository.filter(tenant=tenant).count()
        active_suppliers = self.repository.filter(tenant=tenant, status="active").count()
        preferred_suppliers = self.repository.filter(tenant=tenant, is_preferred=True).count()
        blacklisted_suppliers = self.repository.filter(tenant=tenant, is_blacklisted=True).count()

        return {
            "tenant_id": str(tenant.pk),
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
            "preferred_suppliers": preferred_suppliers,
            "blacklisted_suppliers": blacklisted_suppliers,
        }

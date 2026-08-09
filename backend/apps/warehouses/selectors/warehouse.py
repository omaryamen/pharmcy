"""Warehouse selector functions for tenant, company & branch-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from apps.warehouses.models import Warehouse
from apps.warehouses.repositories import WarehouseRepository


class WarehouseSelector:
    def __init__(self) -> None:
        self.repository = WarehouseRepository()

    def list_warehouses(
        self,
        tenant,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_type: str | None = None,
        status: str | None = None,
        manager_id: str | None = None,
        search: str | None = None,
    ) -> QuerySet[Warehouse]:
        qs = self.repository.filter(tenant=tenant).select_related("company", "branch", "manager", "tenant")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_type:
            qs = qs.filter(warehouse_type=warehouse_type)
        if status:
            qs = qs.filter(status=status)
        if manager_id:
            qs = qs.filter(manager_id=manager_id)

        if search:
            qs = qs.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(arabic_name__icontains=search)
                | Q(english_name__icontains=search)
                | Q(city__icontains=search)
            )

        return qs

    def get_warehouse_detail(self, tenant, warehouse_id: str) -> Warehouse | None:
        return (
            self.repository.filter(tenant=tenant, pk=warehouse_id)
            .select_related("company", "branch", "manager", "tenant")
            .prefetch_related("locations")
            .first()
        )

    def search_warehouses(self, tenant, query: str, limit: int = 20) -> QuerySet[Warehouse]:
        query_clean = query.strip()
        if not query_clean:
            return self.repository.model.objects.none()

        return (
            self.repository.filter(tenant=tenant, status="active")
            .filter(
                Q(code__icontains=query_clean)
                | Q(name__icontains=query_clean)
                | Q(arabic_name__icontains=query_clean)
                | Q(english_name__icontains=query_clean)
                | Q(city__icontains=query_clean)
            )
            .select_related("company", "branch", "manager")[:limit]
        )

    def get_warehouse_stats(self, tenant) -> dict[str, Any]:
        qs = self.repository.filter(tenant=tenant)
        total_warehouses = qs.count()
        active_warehouses = qs.filter(status="active").count()
        suspended_warehouses = qs.filter(status="suspended").count()
        main_warehouses = qs.filter(warehouse_type="main").count()
        branch_warehouses = qs.filter(warehouse_type="branch").count()
        cold_storage_warehouses = qs.filter(warehouse_type="cold_storage").count()

        return {
            "tenant_id": str(tenant.pk),
            "total_warehouses": total_warehouses,
            "active_warehouses": active_warehouses,
            "suspended_warehouses": suspended_warehouses,
            "main_warehouses": main_warehouses,
            "branch_warehouses": branch_warehouses,
            "cold_storage_warehouses": cold_storage_warehouses,
        }

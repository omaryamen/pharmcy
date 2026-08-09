"""Storage Location selector functions for hierarchical location queries."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from apps.warehouses.models import StorageLocation
from apps.warehouses.repositories import StorageLocationRepository


class StorageLocationSelector:
    def __init__(self) -> None:
        self.repository = StorageLocationRepository()

    def list_locations(
        self,
        tenant,
        *,
        warehouse_id: str | None = None,
        parent_id: str | None = None,
        location_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[StorageLocation]:
        qs = self.repository.filter(tenant=tenant).select_related("warehouse", "parent")

        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if parent_id is not None:
            if parent_id == "none" or parent_id == "null":
                qs = qs.filter(parent__isnull=True)
            else:
                qs = qs.filter(parent_id=parent_id)
        if location_type:
            qs = qs.filter(location_type=location_type)
        if status:
            qs = qs.filter(status=status)

        if search:
            qs = qs.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(arabic_name__icontains=search)
                | Q(english_name__icontains=search)
            )

        return qs

    def get_location_detail(self, tenant, location_id: str) -> StorageLocation | None:
        return (
            self.repository.filter(tenant=tenant, pk=location_id)
            .select_related("warehouse", "parent", "tenant")
            .prefetch_related("children")
            .first()
        )

    def get_location_tree(self, tenant, warehouse_id: str) -> list[dict[str, Any]]:
        """Returns recursive hierarchical tree of storage locations for a warehouse."""
        all_locations = list(
            self.repository.filter(tenant=tenant, warehouse_id=warehouse_id)
            .select_related("parent")
            .order_by("display_order", "code")
        )

        nodes_by_id: dict[str, dict[str, Any]] = {}
        for loc in all_locations:
            lid = str(loc.pk)
            nodes_by_id[lid] = {
                "id": lid,
                "code": loc.code,
                "name": loc.name,
                "arabic_name": loc.arabic_name,
                "english_name": loc.english_name,
                "display_name": loc.display_name,
                "location_type": loc.location_type,
                "status": loc.status,
                "full_path": loc.get_full_path(),
                "display_order": loc.display_order,
                "capacity": str(loc.capacity),
                "capacity_unit": loc.capacity_unit,
                "current_utilization": str(loc.current_utilization),
                "storage_conditions": loc.storage_conditions,
                "parent_id": str(loc.parent_id) if loc.parent_id else None,
                "children": [],
            }

        root_nodes: list[dict[str, Any]] = []
        for node in nodes_by_id.values():
            pid = node["parent_id"]
            if pid and pid in nodes_by_id:
                nodes_by_id[pid]["children"].append(node)
            else:
                root_nodes.append(node)

        return root_nodes

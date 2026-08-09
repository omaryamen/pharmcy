"""InventoryItem selector functions for stock balance lookups and recall readiness."""

from __future__ import annotations

from typing import Any

from django.db.models import F, Q, QuerySet, Sum

from apps.inventory.models import InventoryItem
from apps.inventory.repositories import InventoryItemRepository


class InventoryItemSelector:
    def __init__(self) -> None:
        self.repository = InventoryItemRepository()

    def list_inventory_items(
        self,
        tenant,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        storage_location_id: str | None = None,
        medicine_id: str | None = None,
        batch_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[InventoryItem]:
        qs = self.repository.filter(tenant=tenant).select_related(
            "company", "branch", "warehouse", "storage_location", "medicine", "batch", "tenant"
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if storage_location_id:
            qs = qs.filter(storage_location_id=storage_location_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if status:
            qs = qs.filter(status=status)

        if search:
            qs = qs.filter(
                Q(medicine__english_name__icontains=search)
                | Q(medicine__arabic_name__icontains=search)
                | Q(medicine__brand_name__icontains=search)
                | Q(medicine__generic_name__icontains=search)
                | Q(medicine__code__icontains=search)
                | Q(medicine__sku__icontains=search)
                | Q(medicine__barcode__icontains=search)
                | Q(batch__batch_number__icontains=search)
                | Q(warehouse__name__icontains=search)
                | Q(storage_location__code__icontains=search)
            )

        return qs

    def get_inventory_detail(self, tenant, item_id: str) -> InventoryItem | None:
        return (
            self.repository.filter(tenant=tenant, pk=item_id)
            .select_related("company", "branch", "warehouse", "storage_location", "medicine", "batch", "tenant")
            .first()
        )

    def find_inventory_for_recall(self, tenant, *, medicine_id: str | None = None, batch_number: str | None = None) -> QuerySet[InventoryItem]:
        """Recall readiness selector finding all physical stock positions containing a specified medicine/batch."""
        qs = self.repository.filter(tenant=tenant).select_related(
            "warehouse", "storage_location", "medicine", "batch", "company"
        )
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if batch_number:
            qs = qs.filter(batch__batch_number__iexact=batch_number.strip())

        return qs.filter(on_hand_quantity__gt=0)

    def get_stock_summary(self, tenant, *, warehouse_id: str | None = None) -> dict[str, Any]:
        qs = self.repository.filter(tenant=tenant)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        totals = qs.aggregate(
            total_items=Sum(1),
            total_on_hand=Sum("on_hand_quantity"),
            total_reserved=Sum("reserved_quantity"),
            total_damaged=Sum("damaged_quantity"),
            total_quarantine=Sum("quarantine_quantity"),
        )

        return {
            "tenant_id": str(tenant.pk),
            "total_items": totals["total_items"] or 0,
            "total_on_hand": str(totals["total_on_hand"] or "0.00"),
            "total_reserved": str(totals["total_reserved"] or "0.00"),
            "total_damaged": str(totals["total_damaged"] or "0.00"),
            "total_quarantine": str(totals["total_quarantine"] or "0.00"),
        }

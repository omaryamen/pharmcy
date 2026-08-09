"""InventoryTransaction selector functions for stock audit logs and traceability."""

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.inventory.models import InventoryTransaction
from apps.inventory.repositories import InventoryTransactionRepository


class InventoryTransactionSelector:
    def __init__(self) -> None:
        self.repository = InventoryTransactionRepository()

    def list_transactions(
        self,
        tenant,
        *,
        company_id: str | None = None,
        warehouse_id: str | None = None,
        medicine_id: str | None = None,
        batch_id: str | None = None,
        inventory_item_id: str | None = None,
        transaction_type: str | None = None,
        reference_number: str | None = None,
        search: str | None = None,
    ) -> QuerySet[InventoryTransaction]:
        qs = self.repository.filter(tenant=tenant).select_related(
            "company", "branch", "warehouse", "storage_location", "medicine", "batch", "performed_by", "tenant"
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if inventory_item_id:
            qs = qs.filter(inventory_item_id=inventory_item_id)
        if transaction_type:
            qs = qs.filter(transaction_type=transaction_type)
        if reference_number:
            qs = qs.filter(reference_number__icontains=reference_number)

        if search:
            qs = qs.filter(
                Q(medicine__english_name__icontains=search)
                | Q(medicine__arabic_name__icontains=search)
                | Q(batch__batch_number__icontains=search)
                | Q(reference_number__icontains=search)
                | Q(warehouse__name__icontains=search)
            )

        return qs

    def get_transaction_detail(self, tenant, transaction_id: str) -> InventoryTransaction | None:
        return (
            self.repository.filter(tenant=tenant, pk=transaction_id)
            .select_related("company", "branch", "warehouse", "storage_location", "medicine", "batch", "performed_by", "tenant")
            .first()
        )

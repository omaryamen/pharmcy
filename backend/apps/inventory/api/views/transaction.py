"""InventoryTransaction ViewSet for auditable stock movement logs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.inventory.permissions import CanViewTransactions
from apps.inventory.selectors import InventoryTransactionSelector
from apps.inventory.serializers import InventoryTransactionSerializer


@extend_schema_view(
    list=extend_schema(tags=["inventory-transactions"], summary="List auditable stock movement logs"),
    retrieve=extend_schema(tags=["inventory-transactions"], summary="Retrieve stock transaction details"),
)
class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewTransactions]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = InventoryTransactionSelector()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        return self.selector.list_transactions(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            warehouse_id=self.request.query_params.get("warehouse"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_id=self.request.query_params.get("batch"),
            inventory_item_id=self.request.query_params.get("inventory_item"),
            transaction_type=self.request.query_params.get("transaction_type"),
            reference_number=self.request.query_params.get("reference_number"),
            search=self.request.query_params.get("search"),
        )

"""InventoryItem ViewSet for Stock Balance & Adjustment APIs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.inventory.permissions import CanAdjustInventory, CanManageInventory, CanViewInventory
from apps.inventory.selectors import InventoryItemSelector
from apps.inventory.serializers import (
    InventoryItemCreateSerializer,
    InventoryItemDetailSerializer,
    InventoryItemSerializer,
    InventoryTransactionSerializer,
    StockAdjustmentSerializer,
    StockReservationSerializer,
)
from apps.inventory.services import InventoryService


@extend_schema_view(
    list=extend_schema(tags=["inventory"], summary="List stock position balances for active tenant"),
    retrieve=extend_schema(tags=["inventory"], summary="Retrieve stock position detail"),
    create=extend_schema(tags=["inventory"], summary="Create or initialize stock position item"),
)
class InventoryItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = InventoryItemSelector()
        self.service = InventoryService()

    def get_permissions(self):
        if self.action in {"create"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageInventory)()]
        if self.action in {"adjust", "reserve", "release_reservation"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanAdjustInventory)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewInventory)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        return self.selector.list_inventory_items(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            storage_location_id=self.request.query_params.get("storage_location"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_id=self.request.query_params.get("batch"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return InventoryItemCreateSerializer
        if self.action == "retrieve":
            return InventoryItemDetailSerializer
        if self.action == "adjust":
            return StockAdjustmentSerializer
        if self.action in {"reserve", "release_reservation"}:
            return StockReservationSerializer
        return InventoryItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = self.service.get_or_create_inventory_item(
            tenant=request.tenant,
            company=data["company"],
            branch=data.get("branch"),
            warehouse=data["warehouse"],
            storage_location=data["storage_location"],
            medicine=data["medicine"],
            batch=data["batch"],
            unit_cost=data.get("unit_cost", 0.0000),
            selling_price=data.get("selling_price", 0.0000),
            min_quantity=data.get("min_quantity", 0.00),
            max_quantity=data.get("max_quantity", 0.00),
            reorder_point=data.get("reorder_point", 0.00),
        )

        return Response(InventoryItemDetailSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="adjust")
    def adjust(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        updated_item, tx = self.service.adjust_quantity(
            tenant=request.tenant,
            inventory_item_id=str(item.pk),
            quantity_delta=data["quantity_delta"],
            transaction_type=data.get("transaction_type", "adjustment_increase"),
            reason=data.get("reason", "correction"),
            reference_number=data.get("reference_number", ""),
            unit_cost=data.get("unit_cost"),
            performed_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(
            {
                "inventory_item": InventoryItemDetailSerializer(updated_item).data,
                "transaction": InventoryTransactionSerializer(tx).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="reserve")
    def reserve(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        updated_item, tx = self.service.reserve_stock(
            tenant=request.tenant,
            inventory_item_id=str(item.pk),
            requested_quantity=data["requested_quantity"],
            reference_number=data.get("reference_number", ""),
            performed_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(
            {
                "inventory_item": InventoryItemDetailSerializer(updated_item).data,
                "transaction": InventoryTransactionSerializer(tx).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="release-reservation")
    def release_reservation(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        updated_item, tx = self.service.release_reservation(
            tenant=request.tenant,
            inventory_item_id=str(item.pk),
            release_quantity=data["requested_quantity"],
            reference_number=data.get("reference_number", ""),
            performed_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(
            {
                "inventory_item": InventoryItemDetailSerializer(updated_item).data,
                "transaction": InventoryTransactionSerializer(tx).data,
            }
        )

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        data = self.selector.get_stock_summary(request.tenant, warehouse_id=request.query_params.get("warehouse"))
        return Response(data)

    @action(detail=False, methods=["get"], url_path="recall-lookup")
    def recall_lookup(self, request):
        items = self.selector.find_inventory_for_recall(
            request.tenant,
            medicine_id=request.query_params.get("medicine"),
            batch_number=request.query_params.get("batch_number"),
        )
        return Response(InventoryItemSerializer(items, many=True).data)

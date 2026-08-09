"""Storage Location ViewSet for Managing Hierarchical Storage Structures."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.warehouses.exceptions import WarehouseNotFoundError
from apps.warehouses.permissions import CanManageLocations, CanViewLocations
from apps.warehouses.selectors import StorageLocationSelector, WarehouseSelector
from apps.warehouses.serializers import (
    StorageLocationCreateSerializer,
    StorageLocationDetailSerializer,
    StorageLocationMoveSerializer,
    StorageLocationSerializer,
)
from apps.warehouses.services import StorageLocationService


@extend_schema_view(
    list=extend_schema(tags=["storage-locations"], summary="List storage locations for active tenant"),
    retrieve=extend_schema(tags=["storage-locations"], summary="Retrieve storage location details"),
    create=extend_schema(tags=["storage-locations"], summary="Create new storage location"),
    update=extend_schema(tags=["storage-locations"], summary="Update storage location details"),
    partial_update=extend_schema(tags=["storage-locations"], summary="Partially update storage location details"),
    destroy=extend_schema(tags=["storage-locations"], summary="Soft delete storage location"),
)
class StorageLocationViewSet(viewsets.ModelViewSet):
    serializer_class = StorageLocationSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = StorageLocationSelector()
        self.warehouse_selector = WarehouseSelector()
        self.service = StorageLocationService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "move", "activate", "deactivate"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageLocations)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewLocations)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        warehouse_pk = self.kwargs.get("warehouse_pk") or self.request.query_params.get("warehouse")

        return self.selector.list_locations(
            tenant=tenant,
            warehouse_id=warehouse_pk,
            parent_id=self.request.query_params.get("parent"),
            location_type=self.request.query_params.get("location_type"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return StorageLocationCreateSerializer
        if self.action == "retrieve":
            return StorageLocationDetailSerializer
        if self.action == "move":
            return StorageLocationMoveSerializer
        return StorageLocationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = data["warehouse"]
        # Ensure warehouse belongs to request tenant
        if warehouse.tenant_id != request.tenant.id:
            raise WarehouseNotFoundError()

        location = self.service.create_location(
            tenant=request.tenant,
            warehouse=warehouse,
            parent=data.get("parent"),
            code=data["code"],
            name=data["name"],
            arabic_name=data.get("arabic_name", ""),
            english_name=data.get("english_name", ""),
            description=data.get("description", ""),
            location_type=data.get("location_type", "zone"),
            status=data.get("status", "active"),
            display_order=data.get("display_order", 0),
            capacity=data.get("capacity", 0.00),
            capacity_unit=data.get("capacity_unit", "units"),
            current_utilization=data.get("current_utilization", 0.00),
            min_temperature=data.get("min_temperature"),
            max_temperature=data.get("max_temperature"),
            min_humidity=data.get("min_humidity"),
            max_humidity=data.get("max_humidity"),
            storage_conditions=data.get("storage_conditions"),
        )

        return Response(StorageLocationDetailSerializer(location).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        location = self.get_object()
        serializer = self.get_serializer(location, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_location(location, **serializer.validated_data)
        return Response(StorageLocationDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        location = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.service.move_location(location, serializer.validated_data.get("new_parent"))
        return Response(StorageLocationDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        location = self.get_object()
        updated = self.service.activate_location(location)
        return Response(StorageLocationSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        location = self.get_object()
        updated = self.service.deactivate_location(location)
        return Response(StorageLocationSerializer(updated).data)

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request, warehouse_pk=None, *args, **kwargs):
        warehouse_id = warehouse_pk or request.query_params.get("warehouse")
        if not warehouse_id:
            return Response({"error": "Warehouse ID is required for tree view."}, status=status.HTTP_400_BAD_REQUEST)
        tree_data = self.selector.get_location_tree(request.tenant, warehouse_id)
        return Response(tree_data)

    def destroy(self, request, *args, **kwargs):
        location = self.get_object()
        self.service.soft_delete_location(location)
        return Response(status=status.HTTP_204_NO_CONTENT)

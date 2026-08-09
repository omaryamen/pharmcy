"""Warehouse ViewSet for Enterprise Warehouse Management APIs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.warehouses.permissions import CanManageWarehouses, CanViewWarehouses
from apps.warehouses.selectors import WarehouseSelector
from apps.warehouses.serializers import (
    ManagerAssignmentSerializer,
    WarehouseCreateSerializer,
    WarehouseDetailSerializer,
    WarehouseSerializer,
    WarehouseUpdateSerializer,
)
from apps.warehouses.services import WarehouseService


@extend_schema_view(
    list=extend_schema(tags=["warehouses"], summary="List warehouses for active tenant"),
    retrieve=extend_schema(tags=["warehouses"], summary="Retrieve warehouse details"),
    create=extend_schema(tags=["warehouses"], summary="Create new warehouse entity"),
    update=extend_schema(tags=["warehouses"], summary="Update warehouse details"),
    partial_update=extend_schema(tags=["warehouses"], summary="Partially update warehouse details"),
    destroy=extend_schema(tags=["warehouses"], summary="Soft delete warehouse entity"),
)
class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = WarehouseSelector()
        self.service = WarehouseService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "suspend", "close_temporarily", "restore", "assign_manager"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageWarehouses)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewWarehouses)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        return self.selector.list_warehouses(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_type=self.request.query_params.get("warehouse_type"),
            status=self.request.query_params.get("status"),
            manager_id=self.request.query_params.get("manager"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return WarehouseCreateSerializer
        if self.action in {"update", "partial_update"}:
            return WarehouseUpdateSerializer
        if self.action == "retrieve":
            return WarehouseDetailSerializer
        if self.action == "assign_manager":
            return ManagerAssignmentSerializer
        return WarehouseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = self.service.create_warehouse(
            tenant=request.tenant,
            company=data["company"],
            branch=data.get("branch"),
            code=data.get("code"),
            name=data["name"],
            arabic_name=data.get("arabic_name", ""),
            english_name=data.get("english_name", ""),
            description=data.get("description", ""),
            warehouse_type=data.get("warehouse_type", "main"),
            manager=data.get("manager"),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            country=data.get("country", "Yemen"),
            city=data.get("city", "Sanaa"),
            district=data.get("district", ""),
            postal_code=data.get("postal_code", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            working_hours=data.get("working_hours", ""),
            is_default_receiving=data.get("is_default_receiving", False),
            is_default_returns=data.get("is_default_returns", False),
            is_default_quarantine=data.get("is_default_quarantine", False),
            is_default_damaged=data.get("is_default_damaged", False),
            is_default_cold=data.get("is_default_cold", False),
            notes=data.get("notes", ""),
        )

        return Response(WarehouseDetailSerializer(warehouse).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        warehouse = self.get_object()
        serializer = self.get_serializer(warehouse, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_warehouse(warehouse, **serializer.validated_data)
        return Response(WarehouseDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        warehouse = self.get_object()
        updated = self.service.activate_warehouse(warehouse)
        return Response(WarehouseSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        warehouse = self.get_object()
        updated = self.service.deactivate_warehouse(warehouse)
        return Response(WarehouseSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        warehouse = self.get_object()
        updated = self.service.suspend_warehouse(warehouse)
        return Response(WarehouseSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="close-temporarily")
    def close_temporarily(self, request, pk=None):
        warehouse = self.get_object()
        updated = self.service.close_temporarily_warehouse(warehouse)
        return Response(WarehouseSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        warehouse = self.get_object()
        updated = self.service.restore_warehouse(warehouse)
        return Response(WarehouseSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="assign-manager")
    def assign_manager(self, request, pk=None):
        warehouse = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.service.assign_manager(warehouse, serializer.validated_data["manager_id"])
        return Response(WarehouseDetailSerializer(updated).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        stats_data = self.selector.get_warehouse_stats(request.tenant)
        return Response(stats_data)

    @action(detail=False, methods=["get"], url_path="search")
    def fast_search(self, request):
        query = request.query_params.get("q", "").strip()
        warehouses = self.selector.search_warehouses(request.tenant, query)
        return Response(WarehouseSerializer(warehouses, many=True).data)

    def destroy(self, request, *args, **kwargs):
        warehouse = self.get_object()
        self.service.soft_delete_warehouse(warehouse)
        return Response(status=status.HTTP_204_NO_CONTENT)

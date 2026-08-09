"""Batch ViewSet for pharmaceutical lot management APIs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.inventory.permissions import CanManageBatches, CanViewBatches
from apps.inventory.selectors import BatchSelector
from apps.inventory.serializers import (
    BatchCreateSerializer,
    BatchDetailSerializer,
    BatchSerializer,
    BatchUpdateSerializer,
)
from apps.inventory.services import BatchService


@extend_schema_view(
    list=extend_schema(tags=["batches"], summary="List pharmaceutical batches for active tenant"),
    retrieve=extend_schema(tags=["batches"], summary="Retrieve batch details"),
    create=extend_schema(tags=["batches"], summary="Create new batch entity"),
    update=extend_schema(tags=["batches"], summary="Update batch details"),
    partial_update=extend_schema(tags=["batches"], summary="Partially update batch details"),
    destroy=extend_schema(tags=["batches"], summary="Soft delete batch record"),
)
class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = BatchSelector()
        self.service = BatchService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "block", "unblock", "recall"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageBatches)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewBatches)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        return self.selector.list_batches(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            medicine_id=self.request.query_params.get("medicine"),
            supplier_id=self.request.query_params.get("supplier"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BatchCreateSerializer
        if self.action in {"update", "partial_update"}:
            return BatchUpdateSerializer
        if self.action == "retrieve":
            return BatchDetailSerializer
        return BatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        batch = self.service.create_batch(
            tenant=request.tenant,
            company=data["company"],
            medicine=data["medicine"],
            batch_number=data["batch_number"],
            expiry_date=data["expiry_date"],
            supplier=data.get("supplier"),
            lot_number=data.get("lot_number", ""),
            manufacturing_date=data.get("manufacturing_date"),
            registration_number=data.get("registration_number", ""),
            country_of_origin=data.get("country_of_origin", ""),
            status=data.get("status", "active"),
            unit_cost=data.get("unit_cost", 0.0000),
            selling_price=data.get("selling_price", 0.0000),
            initial_quantity=data.get("initial_quantity", 0.00),
            storage_requirements=data.get("storage_requirements", ""),
            notes=data.get("notes", ""),
        )

        return Response(BatchDetailSerializer(batch).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        batch = self.get_object()
        serializer = self.get_serializer(batch, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_batch(batch, **serializer.validated_data)
        return Response(BatchDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="block")
    def block(self, request, pk=None):
        batch = self.get_object()
        updated = self.service.block_batch(batch)
        return Response(BatchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="unblock")
    def unblock(self, request, pk=None):
        batch = self.get_object()
        updated = self.service.unblock_batch(batch)
        return Response(BatchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="recall")
    def recall(self, request, pk=None):
        batch = self.get_object()
        updated = self.service.recall_batch(batch)
        return Response(BatchSerializer(updated).data)

    @action(detail=False, methods=["get"], url_path="expired")
    def expired(self, request):
        batches = self.selector.get_expired_batches(request.tenant, medicine_id=request.query_params.get("medicine"))
        return Response(BatchSerializer(batches, many=True).data)

    @action(detail=False, methods=["get"], url_path="expiring-soon")
    def expiring_soon(self, request):
        days = int(request.query_params.get("days", 90))
        batches = self.selector.get_expiring_soon_batches(
            request.tenant, days=days, medicine_id=request.query_params.get("medicine")
        )
        return Response(BatchSerializer(batches, many=True).data)

    @action(detail=False, methods=["get"], url_path="fefo")
    def fefo_lookup(self, request):
        medicine_id = request.query_params.get("medicine")
        if not medicine_id:
            return Response({"error": "Query parameter 'medicine' is required for FEFO lookup."}, status=status.HTTP_400_BAD_REQUEST)

        batches = self.selector.get_available_batches_fefo(
            request.tenant, medicine_id=medicine_id, warehouse_id=request.query_params.get("warehouse")
        )
        return Response(BatchSerializer(batches, many=True).data)

    def destroy(self, request, *args, **kwargs):
        batch = self.get_object()
        self.service.soft_delete_batch(batch)
        return Response(status=status.HTTP_204_NO_CONTENT)

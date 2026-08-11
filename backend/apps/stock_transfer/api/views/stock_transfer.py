"""REST API ViewSet for Enterprise Stock Transfer management."""

from __future__ import annotations

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.stock_transfer.permissions import (
    CanApproveStockTransfers,
    CanCancelStockTransfers,
    CanCreateStockTransfers,
    CanDispatchStockTransfers,
    CanPickStockTransfers,
    CanReceiveStockTransfers,
    CanReconcileStockTransfers,
    CanRejectStockTransfers,
    CanRequestStockTransfers,
    CanResolveTransferDiscrepancies,
    CanReverseStockTransfers,
    CanViewStockTransfers,
    CanViewTransferDiscrepancies,
)
from apps.stock_transfer.selectors import StockTransferSelector
from apps.stock_transfer.serializers import (
    DiscrepancyResolveSerializer,
    StockTransferApproveSerializer,
    StockTransferCancelSerializer,
    StockTransferCreateSerializer,
    StockTransferDiscrepancySerializer,
    StockTransferDispatchSerializer,
    StockTransferHistorySerializer,
    StockTransferPickSerializer,
    StockTransferReceiveSerializer,
    StockTransferReverseSerializer,
    StockTransferSerializer,
)
from apps.stock_transfer.services import StockTransferService
from apps.warehouses.models import StorageLocation, Warehouse

logger = logging.getLogger(__name__)


class StockTransferViewSet(viewsets.ModelViewSet):
    """API ViewSet providing full CRUD, workflow actions, discrepancy handling, and statistics for Stock Transfers."""

    serializer_class = StockTransferSerializer
    permission_classes = [CanViewStockTransfers]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.serializer_class.Meta.model.objects.none()

        selector = StockTransferSelector()
        return selector.list_transfers(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            source_branch_id=self.request.query_params.get("source_branch"),
            destination_branch_id=self.request.query_params.get("destination_branch"),
            source_warehouse_id=self.request.query_params.get("source_warehouse"),
            destination_warehouse_id=self.request.query_params.get("destination_warehouse"),
            transfer_type=self.request.query_params.get("transfer_type"),
            status=self.request.query_params.get("status"),
            priority=self.request.query_params.get("priority"),
            created_by_id=self.request.query_params.get("created_by"),
            date_from=self.request.query_params.get("date_from"),
            date_to=self.request.query_params.get("date_to"),
            search=self.request.query_params.get("search"),
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [CanCreateStockTransfers()]
        elif self.action in ["request"]:
            return [CanRequestStockTransfers()]
        elif self.action in ["approve"]:
            return [CanApproveStockTransfers()]
        elif self.action in ["pick"]:
            return [CanPickStockTransfers()]
        elif self.action in ["dispatch"]:
            return [CanDispatchStockTransfers()]
        elif self.action in ["receive"]:
            return [CanReceiveStockTransfers()]
        elif self.action in ["reject"]:
            return [CanRejectStockTransfers()]
        elif self.action in ["cancel"]:
            return [CanCancelStockTransfers()]
        elif self.action in ["reconcile"]:
            return [CanReconcileStockTransfers()]
        elif self.action in ["reverse"]:
            return [CanReverseStockTransfers()]
        elif self.action in ["discrepancies"]:
            return [CanViewTransferDiscrepancies()]
        elif self.action in ["resolve_discrepancy"]:
            return [CanResolveTransferDiscrepancies()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        tenant = getattr(request, "tenant", None)
        serializer = StockTransferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = Company.objects.get(pk=data["company"], tenant=tenant)
        src_wh = Warehouse.objects.get(pk=data["source_warehouse"], tenant=tenant)
        dst_wh = Warehouse.objects.get(pk=data["destination_warehouse"], tenant=tenant)

        src_branch = Branch.objects.filter(pk=data.get("source_branch"), tenant=tenant).first() if data.get("source_branch") else None
        dst_branch = Branch.objects.filter(pk=data.get("destination_branch"), tenant=tenant).first() if data.get("destination_branch") else None
        src_loc = StorageLocation.objects.filter(pk=data.get("source_location"), tenant=tenant).first() if data.get("source_location") else None
        dst_loc = StorageLocation.objects.filter(pk=data.get("destination_location"), tenant=tenant).first() if data.get("destination_location") else None

        lines_payload = []
        for line_item in data["lines"]:
            med = Medicine.objects.get(pk=line_item["medicine_id"], tenant=tenant)
            batch = Batch.objects.filter(pk=line_item.get("batch_id"), tenant=tenant).first() if line_item.get("batch_id") else None
            line_src_loc = StorageLocation.objects.filter(pk=line_item.get("source_location_id"), tenant=tenant).first() if line_item.get("source_location_id") else src_loc
            line_dst_loc = StorageLocation.objects.filter(pk=line_item.get("destination_location_id"), tenant=tenant).first() if line_item.get("destination_location_id") else dst_loc

            lines_payload.append({
                "medicine": med,
                "batch": batch,
                "source_location": line_src_loc,
                "destination_location": line_dst_loc,
                "requested_quantity": line_item["requested_quantity"],
                "unit": line_item.get("unit", "Pcs"),
                "unit_cost": line_item.get("unit_cost", "0.0000"),
                "notes": line_item.get("notes", ""),
            })

        service = StockTransferService()
        transfer = service.create_transfer(
            tenant=tenant,
            company=company,
            source_warehouse=src_wh,
            destination_warehouse=dst_wh,
            lines_data=lines_payload,
            source_branch=src_branch,
            destination_branch=dst_branch,
            source_location=src_loc,
            destination_location=dst_loc,
            transfer_type=data.get("transfer_type", "warehouse_transfer"),
            priority=data.get("priority", "medium"),
            expected_arrival_date=data.get("expected_arrival_date"),
            reason=data.get("reason", ""),
            notes=data.get("notes", ""),
            reference_type=data.get("reference_type", ""),
            reference_id=data.get("reference_id", ""),
            idempotency_key=data.get("idempotency_key", ""),
            user=request.user,
        )

        out_serializer = StockTransferSerializer(transfer, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="request")
    def request_transfer(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        service = StockTransferService()
        updated = service.request_transfer(tenant, transfer, user=request.user)
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = StockTransferService()
        updated = service.approve_transfer(
            tenant, transfer, user=request.user, approved_lines=serializer.validated_data.get("lines")
        )
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="pick")
    def pick(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferPickSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        picking_payload = []
        if serializer.validated_data.get("lines"):
            for p_line in serializer.validated_data["lines"]:
                batch_obj = Batch.objects.filter(pk=p_line.get("batch_id"), tenant=tenant).first() if p_line.get("batch_id") else None
                picking_payload.append({
                    "line_id": p_line["line_id"],
                    "batch": batch_obj,
                    "picked_quantity": p_line["picked_quantity"],
                })

        service = StockTransferService()
        updated = service.pick_transfer(
            tenant, transfer, picking_data=picking_payload if picking_payload else None, user=request.user
        )
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="dispatch")
    def dispatch(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferDispatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dispatch_payload = serializer.validated_data.get("lines")
        idempotency_key = serializer.validated_data.get("idempotency_key", "")

        service = StockTransferService()
        updated = service.dispatch_transfer(
            tenant, transfer, dispatch_lines=dispatch_payload, user=request.user, idempotency_key=idempotency_key
        )
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receive_payload = []
        for r_line in serializer.validated_data["lines"]:
            dst_loc = StorageLocation.objects.filter(pk=r_line.get("destination_location_id"), tenant=tenant).first() if r_line.get("destination_location_id") else None
            rx_med = Medicine.objects.filter(pk=r_line.get("received_medicine_id"), tenant=tenant).first() if r_line.get("received_medicine_id") else None
            rx_batch = Batch.objects.filter(pk=r_line.get("received_batch_id"), tenant=tenant).first() if r_line.get("received_batch_id") else None

            receive_payload.append({
                "line_id": r_line["line_id"],
                "destination_location": dst_loc,
                "received_quantity": r_line.get("received_quantity", "0.0000"),
                "damaged_quantity": r_line.get("damaged_quantity", "0.0000"),
                "rejected_quantity": r_line.get("rejected_quantity", "0.0000"),
                "received_medicine": rx_med,
                "received_batch": rx_batch,
                "damage_reason": r_line.get("damage_reason", ""),
            })

        service = StockTransferService()
        updated = service.receive_transfer(tenant, transfer, receive_lines_data=receive_payload, user=request.user)
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        reason = request.data.get("reason", "Transfer request rejected.")
        service = StockTransferService()
        updated = service.reject_transfer(tenant, transfer, reason=reason, user=request.user)
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = StockTransferService()
        updated = service.cancel_transfer(
            tenant, transfer, reason=serializer.validated_data["reason"], user=request.user
        )
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        serializer = StockTransferReverseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = StockTransferService()
        updated = service.reverse_transfer(
            tenant, transfer, reason=serializer.validated_data["reason"], user=request.user
        )
        return Response(StockTransferSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="discrepancies")
    def discrepancies(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        selector = StockTransferSelector()
        discrepancies = selector.get_discrepancies(tenant, transfer_id=str(transfer.pk))
        return Response(StockTransferDiscrepancySerializer(discrepancies, many=True).data)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        transfer = self.get_object()
        selector = StockTransferSelector()
        logs = selector.get_transfer_history(tenant, transfer_id=str(transfer.pk))
        return Response(StockTransferHistorySerializer(logs, many=True).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def statistics(self, request):
        tenant = getattr(request, "tenant", None)
        selector = StockTransferSelector()
        stats = selector.get_transfer_statistics(
            tenant=tenant,
            company_id=request.query_params.get("company"),
            warehouse_id=request.query_params.get("warehouse"),
        )
        return Response(stats)

    @action(detail=True, methods=["post"], url_path="resolve-discrepancy")
    def resolve_discrepancy(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        discrepancy_id = request.data.get("discrepancy_id")
        serializer = DiscrepancyResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selector = StockTransferSelector()
        discrepancy = selector.get_discrepancies(tenant, transfer_id=pk).filter(pk=discrepancy_id).first()
        if not discrepancy:
            return Response({"error": "Discrepancy record not found."}, status=status.HTTP_404_NOT_FOUND)

        service = StockTransferService()
        resolved = service.reconcile_discrepancy(
            tenant, discrepancy, resolution=serializer.validated_data["resolution"], user=request.user
        )
        return Response(StockTransferDiscrepancySerializer(resolved).data)

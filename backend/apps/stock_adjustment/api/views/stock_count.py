"""API ViewSet for managing Enterprise Stock Counts, variance audits, and reconciliation."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.stock_adjustment.permissions import (
    CanApproveStockCounts,
    CanCancelStockCounts,
    CanCreateStockCounts,
    CanPerformStockCounts,
    CanReconcileStockCounts,
    CanRequestRecount,
    CanReviewStockCounts,
    CanStartStockCounts,
    CanSubmitStockCounts,
    CanViewStockCounts,
)
from apps.stock_adjustment.selectors import StockCountSelector
from apps.stock_adjustment.serializers import (
    StockCountCreateSerializer,
    StockCountHistorySerializer,
    StockCountLineSerializer,
    StockCountReconcileSerializer,
    StockCountRecordLinesSerializer,
    StockCountRecountRequestSerializer,
    StockCountRejectSerializer,
    StockCountSerializer,
)
from apps.stock_adjustment.services import StockCountService


class StockCountViewSet(viewsets.ModelViewSet):
    """ViewSet for inventory physical stock count operations and variance reconciliation."""

    serializer_class = StockCountSerializer
    permission_classes = [CanViewStockCounts]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return StockCountSerializer.Meta.model.objects.none()

        selector = StockCountSelector()
        return selector.list_counts(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            count_type=self.request.query_params.get("count_type"),
            count_status=self.request.query_params.get("count_status"),
            created_by_id=self.request.query_params.get("created_by"),
            date_from=self.request.query_params.get("date_from"),
            date_to=self.request.query_params.get("date_to"),
            search=self.request.query_params.get("search"),
        )

    def create(self, request, *args, **kwargs):
        self.permission_classes = [CanCreateStockCounts]
        self.check_permissions(request)

        tenant = getattr(request, "tenant", None)
        serializer = StockCountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = StockCountService()
        stock_count = service.create_stock_count(
            tenant=tenant,
            company=data["company"],
            branch=data.get("branch"),
            warehouse=data["warehouse"],
            storage_location=data.get("storage_location"),
            count_type=data.get("count_type", "warehouse_count"),
            count_scope_type=data.get("count_scope_type", "warehouse"),
            scope_filter=data.get("scope_filter", {}),
            is_blind_count=data.get("is_blind_count", False),
            freeze_inventory=data.get("freeze_inventory", False),
            reason=data.get("reason", ""),
            notes=data.get("notes", ""),
            idempotency_key=data.get("idempotency_key", ""),
            created_by=request.user,
        )

        output_serializer = StockCountSerializer(stock_count, context={"request": request})
        return Response({"status": "success", "data": output_serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[CanViewStockCounts])
    def lines(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        lines_qs = stock_count.lines.select_related("medicine", "batch", "storage_location")
        page = self.paginate_queryset(lines_qs)
        if page is not None:
            serializer = StockCountLineSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = StockCountLineSerializer(lines_qs, many=True, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanStartStockCounts])
    def start(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        service = StockCountService()
        started = service.start_stock_count(tenant, stock_count, user=request.user)

        serializer = StockCountSerializer(started, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanPerformStockCounts], url_path="record-lines")
    def record_lines(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockCountRecordLinesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = StockCountService()
        updated = service.record_count_lines(tenant, stock_count, serializer.validated_data["lines"], user=request.user)

        out = StockCountSerializer(updated, context={"request": request})
        return Response({"status": "success", "data": out.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanSubmitStockCounts])
    def submit(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        service = StockCountService()
        submitted = service.submit_stock_count(tenant, stock_count, user=request.user)

        serializer = StockCountSerializer(submitted, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanRequestRecount])
    def recount(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockCountRecountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = StockCountService()
        recount_doc = service.request_recount(
            tenant=tenant,
            stock_count=stock_count,
            line_ids=[str(i) for i in data["line_ids"]],
            reason=data["reason"],
            user=request.user,
        )

        serializer = StockCountSerializer(recount_doc, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanApproveStockCounts])
    def approve(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        service = StockCountService()
        approved = service.approve_stock_count(tenant, stock_count, user=request.user)

        serializer = StockCountSerializer(approved, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanReconcileStockCounts])
    def reconcile(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockCountReconcileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idem_key = serializer.validated_data.get("idempotency_key", "")

        service = StockCountService()
        reconciled = service.reconcile_stock_count(tenant, stock_count, user=request.user, idempotency_key=idem_key)

        serializer = StockCountSerializer(reconciled, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanCancelStockCounts])
    def cancel(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        stock_count = selector.get_count_by_id(tenant, pk)
        if not stock_count:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        service = StockCountService()
        cancelled = service.cancel_stock_count(tenant, stock_count, user=request.user)

        serializer = StockCountSerializer(cancelled, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[CanViewStockCounts])
    def variance(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        summary = selector.get_count_variance_summary(tenant, pk)
        if not summary:
            return Response({"status": "error", "message": "Stock count not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "success", "data": summary}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[CanViewStockCounts])
    def history(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockCountSelector()
        events = selector.get_count_history(tenant, pk)
        serializer = StockCountHistorySerializer(events, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

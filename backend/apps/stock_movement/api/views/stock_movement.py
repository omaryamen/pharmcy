"""API ViewSet and operational endpoints for Enterprise Stock Movement Engine."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.companies.models import Company
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.stock_movement.permissions import (
    CanCancelStockMovements,
    CanCreateStockMovements,
    CanIssueStock,
    CanProcessStockMovements,
    CanReceiveStock,
    CanReverseStockMovements,
    CanTransferStock,
    CanViewStockMovements,
    CanViewStockTraceability,
)
from apps.stock_movement.selectors import StockMovementSelector
from apps.stock_movement.serializers import (
    IssueStockOperationSerializer,
    ReceiveStockOperationSerializer,
    StockMovementCreateSerializer,
    StockMovementReverseSerializer,
    StockMovementSerializer,
    TransferStockOperationSerializer,
)
from apps.stock_movement.services import StockMovementEngine
from apps.warehouses.models import StorageLocation, Warehouse


class StockMovementViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing and processing Enterprise Stock Movements."""

    serializer_class = StockMovementSerializer
    permission_classes = [CanViewStockMovements]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return StockMovementSerializer.Meta.model.objects.none()

        selector = StockMovementSelector()
        return selector.list_movements(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            source_warehouse_id=self.request.query_params.get("source_warehouse"),
            destination_warehouse_id=self.request.query_params.get("destination_warehouse"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_id=self.request.query_params.get("batch"),
            movement_type=self.request.query_params.get("movement_type"),
            movement_status=self.request.query_params.get("movement_status"),
            reference_type=self.request.query_params.get("reference_type"),
            reference_id=self.request.query_params.get("reference_id"),
            date_from=self.request.query_params.get("date_from"),
            date_to=self.request.query_params.get("date_to"),
            search=self.request.query_params.get("search"),
        )

    def create(self, request, *args, **kwargs):
        self.permission_classes = [CanCreateStockMovements]
        self.check_permissions(request)

        tenant = getattr(request, "tenant", None)
        serializer = StockMovementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        lines_data = data.get("lines", [])
        engine = StockMovementEngine()
        movement = engine.create_movement(
            tenant=tenant,
            company=data["company"],
            branch=data.get("branch"),
            warehouse=data["warehouse"],
            source_warehouse=data.get("source_warehouse"),
            destination_warehouse=data.get("destination_warehouse"),
            source_location=data.get("source_location"),
            destination_location=data.get("destination_location"),
            medicine=data.get("medicine"),
            batch=data.get("batch"),
            movement_type=data["movement_type"],
            quantity=data.get("quantity", 0),
            unit_cost=data.get("unit_cost", 0),
            reference_type=data.get("reference_type", ""),
            reference_id=data.get("reference_id", ""),
            reference_number=data.get("reference_number", ""),
            reason=data.get("reason", ""),
            notes=data.get("notes", ""),
            idempotency_key=data.get("idempotency_key", ""),
            performed_by=request.user,
            lines=lines_data,
            auto_process=data.get("auto_process", False),
        )

        output_serializer = StockMovementSerializer(movement, context={"request": request})
        return Response({"status": "success", "data": output_serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[CanProcessStockMovements])
    def process(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockMovementSelector()
        movement = selector.get_movement_by_id(tenant, pk)
        if not movement:
            return Response({"status": "error", "message": "Stock movement not found."}, status=status.HTTP_404_NOT_FOUND)

        engine = StockMovementEngine()
        processed = engine.process_movement(tenant, movement, performed_by=request.user)

        serializer = StockMovementSerializer(processed, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanCancelStockMovements])
    def cancel(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockMovementSelector()
        movement = selector.get_movement_by_id(tenant, pk)
        if not movement:
            return Response({"status": "error", "message": "Stock movement not found."}, status=status.HTTP_404_NOT_FOUND)

        movement.mark_cancelled(user=request.user)
        serializer = StockMovementSerializer(movement, context={"request": request})
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanReverseStockMovements])
    def reverse(self, request, pk=None):
        tenant = getattr(request, "tenant", None)
        selector = StockMovementSelector()
        movement = selector.get_movement_by_id(tenant, pk)
        if not movement:
            return Response({"status": "error", "message": "Stock movement not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockMovementReverseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get("reason", "")

        engine = StockMovementEngine()
        reversal = engine.reverse_movement(tenant, movement, user=request.user, reason=reason)

        output_serializer = StockMovementSerializer(reversal, context={"request": request})
        return Response({"status": "success", "data": output_serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[CanReceiveStock], url_path="receive")
    def receive(self, request):
        tenant = getattr(request, "tenant", None)
        serializer = ReceiveStockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = Company.objects.get(tenant=tenant, pk=data["company"])
        warehouse = Warehouse.objects.get(tenant=tenant, pk=data["warehouse"])
        location = StorageLocation.objects.get(tenant=tenant, pk=data["location"])
        medicine = Medicine.objects.get(tenant=tenant, pk=data["medicine"])
        batch = Batch.objects.get(tenant=tenant, pk=data["batch"]) if data.get("batch") else None

        engine = StockMovementEngine()
        movement = engine.receive_stock(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            location=location,
            medicine=medicine,
            batch=batch,
            quantity=data["quantity"],
            unit_cost=data.get("unit_cost", 0),
            reference_number=data.get("reference_number", ""),
            performed_by=request.user,
            idempotency_key=data.get("idempotency_key", ""),
        )

        out = StockMovementSerializer(movement, context={"request": request})
        return Response({"status": "success", "data": out.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[CanIssueStock], url_path="issue")
    def issue(self, request):
        tenant = getattr(request, "tenant", None)
        serializer = IssueStockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = Company.objects.get(tenant=tenant, pk=data["company"])
        warehouse = Warehouse.objects.get(tenant=tenant, pk=data["warehouse"])
        location = StorageLocation.objects.get(tenant=tenant, pk=data["location"])
        medicine = Medicine.objects.get(tenant=tenant, pk=data["medicine"])
        batch = Batch.objects.get(tenant=tenant, pk=data["batch"]) if data.get("batch") else None

        engine = StockMovementEngine()
        movement = engine.issue_stock(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            location=location,
            medicine=medicine,
            batch=batch,
            quantity=data["quantity"],
            reference_number=data.get("reference_number", ""),
            performed_by=request.user,
            idempotency_key=data.get("idempotency_key", ""),
        )

        out = StockMovementSerializer(movement, context={"request": request})
        return Response({"status": "success", "data": out.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[CanTransferStock], url_path="transfer")
    def transfer(self, request):
        tenant = getattr(request, "tenant", None)
        serializer = TransferStockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = Company.objects.get(tenant=tenant, pk=data["company"])
        src_wh = Warehouse.objects.get(tenant=tenant, pk=data["source_warehouse"])
        dst_wh = Warehouse.objects.get(tenant=tenant, pk=data["destination_warehouse"])
        src_loc = StorageLocation.objects.get(tenant=tenant, pk=data["source_location"])
        dst_loc = StorageLocation.objects.get(tenant=tenant, pk=data["destination_location"])
        medicine = Medicine.objects.get(tenant=tenant, pk=data["medicine"])
        batch = Batch.objects.get(tenant=tenant, pk=data["batch"]) if data.get("batch") else None

        engine = StockMovementEngine()
        movement = engine.transfer_stock(
            tenant=tenant,
            company=company,
            source_warehouse=src_wh,
            destination_warehouse=dst_wh,
            source_location=src_loc,
            destination_location=dst_loc,
            medicine=medicine,
            batch=batch,
            quantity=data["quantity"],
            reference_number=data.get("reference_number", ""),
            performed_by=request.user,
            idempotency_key=data.get("idempotency_key", ""),
        )

        out = StockMovementSerializer(movement, context={"request": request})
        return Response({"status": "success", "data": out.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], permission_classes=[CanViewStockTraceability], url_path="traceability")
    def traceability(self, request):
        tenant = getattr(request, "tenant", None)
        med_id = request.query_params.get("medicine")
        batch_id = request.query_params.get("batch")

        selector = StockMovementSelector()
        if med_id:
            lines = selector.get_medicine_traceability(tenant, med_id)
        elif batch_id:
            lines = selector.get_batch_traceability(tenant, batch_id)
        else:
            return Response({"status": "error", "message": "Specify 'medicine' or 'batch' query param."}, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(lines)
        if page is not None:
            from apps.stock_movement.serializers.stock_movement_line import StockMovementLineSerializer
            serializer = StockMovementLineSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        from apps.stock_movement.serializers.stock_movement_line import StockMovementLineSerializer
        serializer = StockMovementLineSerializer(lines, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[CanViewStockMovements], url_path="stats")
    def stats(self, request):
        tenant = getattr(request, "tenant", None)
        company_id = request.query_params.get("company")
        warehouse_id = request.query_params.get("warehouse")

        selector = StockMovementSelector()
        stats_data = selector.get_movement_statistics(tenant, company_id=company_id, warehouse_id=warehouse_id)
        return Response({"status": "success", "data": stats_data}, status=status.HTTP_200_OK)

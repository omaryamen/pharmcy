"""REST API ViewSet for CustomerReceivable subledger management."""

from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_receivable.api.serializers import (
    CreateAdjustmentSerializer,
    CreateDisputeSerializer,
    CreateWriteOffSerializer,
    CustomerReceivableSerializer,
    ReceivableAdjustmentSerializer,
    ReceivableDisputeSerializer,
    ReceivableWriteOffSerializer,
    ResolveDisputeSerializer,
    SyncReceivableSerializer,
)
from apps.accounts_receivable.selectors import ReceivableSelector
from apps.accounts_receivable.services import (
    CustomerReceivableService,
    ReceivableAdjustmentService,
    ReceivableDisputeService,
)
from apps.sales.models import SalesInvoice


class CustomerReceivableViewSet(viewsets.ModelViewSet):
    """ViewSet managing CustomerReceivable records, sync from POS sales, adjustments, write-offs, and disputes."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerReceivableSerializer
    selector = ReceivableSelector()
    ar_service = CustomerReceivableService()
    adj_service = ReceivableAdjustmentService()
    dsp_service = ReceivableDisputeService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_receivables(
            tenant=tenant,
            customer_id=self.request.query_params.get("customer_id"),
            status=self.request.query_params.get("status"),
            is_overdue=self.request.query_params.get("is_overdue") == "true",
            search=self.request.query_params.get("search"),
        )

    @action(detail=False, methods=["post"], url_path="sync")
    def sync_from_invoice(self, request: Request) -> Response:
        serializer = SyncReceivableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        invoice = SalesInvoice.objects.get(pk=data["sales_invoice_id"], tenant=tenant)

        receivable = self.ar_service.sync_receivable_from_sales_invoice(
            tenant=tenant,
            sales_invoice=invoice,
            due_days=data.get("due_days", 30),
            idempotency_key=data.get("idempotency_key", ""),
            user=request.user,
        )
        return Response(CustomerReceivableSerializer(receivable).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="adjust")
    def adjust(self, request: Request, pk: str = None) -> Response:
        serializer = CreateAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        rx = self.get_object()

        adj = self.adj_service.create_adjustment(
            tenant=tenant,
            receivable=rx,
            amount=data["amount"],
            adjustment_type=data.get("adjustment_type", "credit_adjustment"),
            reason=data["reason"],
            reference=data.get("reference", ""),
            user=request.user,
        )
        return Response(ReceivableAdjustmentSerializer(adj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="write-off")
    def write_off(self, request: Request, pk: str = None) -> Response:
        serializer = CreateWriteOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        rx = self.get_object()

        wof = self.adj_service.write_off_receivable(
            tenant=tenant,
            receivable=rx,
            amount=data["amount"],
            reason=data["reason"],
            approver=request.user,
            user=request.user,
        )
        return Response(ReceivableWriteOffSerializer(wof).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="dispute")
    def dispute(self, request: Request, pk: str = None) -> Response:
        serializer = CreateDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        rx = self.get_object()

        dsp = self.dsp_service.log_dispute(
            tenant=tenant,
            receivable=rx,
            dispute_amount=data["dispute_amount"],
            reason=data.get("reason", "wrong_amount"),
            description=data["description"],
            user=request.user,
        )
        return Response(ReceivableDisputeSerializer(dsp).data, status=status.HTTP_201_CREATED)

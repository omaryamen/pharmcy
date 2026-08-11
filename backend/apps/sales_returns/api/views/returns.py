"""REST API ViewSet for Customer Return documents."""

from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.sales.models import SalesInvoice
from apps.sales_returns.api.serializers import (
    CustomerRefundCreateSerializer,
    CustomerRefundSerializer,
    CustomerReturnCreateSerializer,
    CustomerReturnSerializer,
    ReturnInspectionSerializer,
)
from apps.sales_returns.models import CustomerReturn
from apps.sales_returns.selectors import ReturnsSelector
from apps.sales_returns.services import CustomerReturnService


class CustomerReturnViewSet(viewsets.ModelViewSet):
    """ViewSet managing Customer Returns, inspection, acceptance, and refund disbursements."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerReturnSerializer
    selector = ReturnsSelector()
    service = CustomerReturnService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_customer_returns(
            tenant=tenant,
            search=self.request.query_params.get("search"),
            status=self.request.query_params.get("status"),
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = CustomerReturnCreateSerializer(data=request.data)
        serializer.is_validate_or_fail() if hasattr(serializer, "is_validate_or_fail") else serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        invoice = SalesInvoice.objects.get(pk=data["sales_invoice_id"], tenant=tenant)

        customer_return = self.service.create_customer_return(
            tenant=tenant,
            sales_invoice=invoice,
            lines_data=data["lines"],
            return_reason=data.get("return_reason", "other"),
            user=request.user,
            idempotency_key=data.get("idempotency_key", ""),
            notes=data.get("notes", ""),
        )
        return Response(CustomerReturnSerializer(customer_return).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        ret = self.get_object()
        approved = self.service.approve_customer_return(tenant, ret, user=request.user)
        return Response(CustomerReturnSerializer(approved).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="inspect")
    def inspect(self, request: Request, pk: str = None) -> Response:
        serializer = ReturnInspectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = getattr(request.user, "tenant", None)
        ret = self.get_object()

        inspected = self.service.inspect_and_accept_return(
            tenant=tenant,
            customer_return=ret,
            inspection_data=serializer.validated_data["inspection_lines"],
            inspector=request.user,
        )
        return Response(CustomerReturnSerializer(inspected).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="process-refund")
    def process_refund(self, request: Request, pk: str = None) -> Response:
        serializer = CustomerRefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        tenant = getattr(request.user, "tenant", None)
        ret = self.get_object()

        refund = self.service.process_customer_refund(
            tenant=tenant,
            customer_return=ret,
            refund_method=data["refund_method"],
            amount=data["amount"],
            user=request.user,
            reference_number=data.get("reference_number", ""),
            notes=data.get("notes", ""),
        )
        return Response(CustomerRefundSerializer(refund).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        ret = self.get_object()
        reason = request.data.get("reason", "")
        reversed_ret = self.service.reverse_customer_return(tenant, ret, user=request.user, reason=reason)
        return Response(CustomerReturnSerializer(reversed_ret).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        stats = self.selector.get_return_analytics(tenant=tenant)
        return Response(stats, status=status.HTTP_200_OK)

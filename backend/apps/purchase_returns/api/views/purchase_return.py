"""REST API ViewSet for PurchaseReturn management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.purchase_returns.api.serializers import (
    PurchaseReturnSerializer,
    SupplierAcceptanceRequestSerializer,
)
from apps.purchase_returns.selectors import PurchaseReturnSelector
from apps.purchase_returns.services import PurchaseReturnService


class PurchaseReturnViewSet(viewsets.ModelViewSet):
    """API endpoints for Purchase Returns, approvals, dispatching, supplier acceptance, discrepancies, and reversals."""

    serializer_class = PurchaseReturnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = PurchaseReturnSelector()
        self.return_service = PurchaseReturnService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_purchase_returns(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            supplier_id=self.request.query_params.get("supplier"),
            goods_receipt_id=self.request.query_params.get("goods_receipt"),
            purchase_order_id=self.request.query_params.get("purchase_order"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_id=self.request.query_params.get("batch"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        purchase_return = self.return_service.create_purchase_return(
            tenant=tenant,
            company=serializer.validated_data["company"],
            supplier=serializer.validated_data["supplier"],
            warehouse=serializer.validated_data["warehouse"],
            lines_data=lines_raw,
            branch=serializer.validated_data.get("branch"),
            purchase_order=serializer.validated_data.get("purchase_order"),
            goods_receipt=serializer.validated_data.get("goods_receipt"),
            return_date=serializer.validated_data.get("return_date"),
            return_reason=serializer.validated_data.get("return_reason"),
            priority=serializer.validated_data.get("priority"),
            currency=serializer.validated_data.get("currency", "USD"),
            exchange_rate=serializer.validated_data.get("exchange_rate", "1.000000"),
            other_charges=serializer.validated_data.get("other_charges", "0.0000"),
            notes=serializer.validated_data.get("notes", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            user=self.request.user,
        )
        serializer.instance = purchase_return

    @action(detail=True, methods=["post"], url_path="request")
    def request_return(self, request: Request, pk: str = None) -> Response:
        """Submit a DRAFT purchase return for approval."""
        tenant = getattr(request, "tenant", None)
        ret = self.selector.get_purchase_return_by_id(tenant, pk)
        if not ret:
            return Response({"detail": "Purchase Return not found."}, status=status.HTTP_404_NOT_FOUND)

        req_ret = self.return_service.request_purchase_return(tenant, ret, user=request.user)
        return Response(self.get_serializer(req_ret).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        """Approve a pending purchase return."""
        tenant = getattr(request, "tenant", None)
        ret = self.selector.get_purchase_return_by_id(tenant, pk)
        if not ret:
            return Response({"detail": "Purchase Return not found."}, status=status.HTTP_404_NOT_FOUND)

        app_ret = self.return_service.approve_purchase_return(tenant, ret, user=request.user)
        return Response(self.get_serializer(app_ret).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="dispatch")
    def dispatch(self, request: Request, pk: str = None) -> Response:
        """DISPATCH ENGINE: Physical stock removal via StockMovementEngine and dispatch to supplier."""
        tenant = getattr(request, "tenant", None)
        ret = self.selector.get_purchase_return_by_id(tenant, pk)
        if not ret:
            return Response({"detail": "Purchase Return not found."}, status=status.HTTP_404_NOT_FOUND)

        disp_ret = self.return_service.dispatch_purchase_return(tenant, ret, user=request.user)
        return Response(self.get_serializer(disp_ret).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="supplier-acceptance")
    def supplier_acceptance(self, request: Request, pk: str = None) -> Response:
        """Record supplier acceptance/rejection, creating ReturnDiscrepancies and SupplierCreditNote where required."""
        tenant = getattr(request, "tenant", None)
        ret = self.selector.get_purchase_return_by_id(tenant, pk)
        if not ret:
            return Response({"detail": "Purchase Return not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SupplierAcceptanceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        acc_ret = self.return_service.record_supplier_acceptance(
            tenant=tenant,
            purchase_return=ret,
            line_acceptances=serializer.validated_data["line_acceptances"],
            supplier_reference=serializer.validated_data.get("supplier_reference", ""),
            user=request.user,
        )
        return Response(self.get_serializer(acc_ret).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        """Reverse a dispatched return, executing compensating stock movements to restore inventory."""
        tenant = getattr(request, "tenant", None)
        ret = self.selector.get_purchase_return_by_id(tenant, pk)
        if not ret:
            return Response({"detail": "Purchase Return not found."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get("reason", "")
        rev_ret = self.return_service.reverse_purchase_return(tenant, ret, reason=reason, user=request.user)
        return Response(self.get_serializer(rev_ret).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        """Get purchase return statistics summary."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_return_statistics(tenant, company_id=request.query_params.get("company"))
        return Response(stats, status=status.HTTP_200_OK)

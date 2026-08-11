"""REST API ViewSet for PurchaseOrder management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.procurement.api.serializers import (
    PurchaseOrderAmendRequestSerializer,
    PurchaseOrderCancelRequestSerializer,
    PurchaseOrderSerializer,
)
from apps.procurement.selectors import PurchaseOrderSelector
from apps.procurement.services import PurchaseOrderService


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """API endpoints for Purchase Orders, approvals, amendments, cancellations, and statistics."""

    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = PurchaseOrderSelector()
        self.po_service = PurchaseOrderService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_purchase_orders(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            supplier_id=self.request.query_params.get("supplier"),
            medicine_id=self.request.query_params.get("medicine"),
            status=self.request.query_params.get("status"),
            priority=self.request.query_params.get("priority"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        po = self.po_service.create_purchase_order(
            tenant=tenant,
            company=serializer.validated_data["company"],
            supplier=serializer.validated_data["supplier"],
            warehouse=serializer.validated_data["warehouse"],
            lines_data=lines_raw,
            branch=serializer.validated_data.get("branch"),
            supplier_reference=serializer.validated_data.get("supplier_reference", ""),
            order_date=serializer.validated_data.get("order_date"),
            expected_delivery_date=serializer.validated_data.get("expected_delivery_date"),
            currency=serializer.validated_data.get("currency", "USD"),
            exchange_rate=serializer.validated_data.get("exchange_rate", "1.000000"),
            payment_terms=serializer.validated_data.get("payment_terms", "Net 30"),
            priority=serializer.validated_data.get("priority"),
            shipping_cost=serializer.validated_data.get("shipping_cost", "0.0000"),
            other_charges=serializer.validated_data.get("other_charges", "0.0000"),
            notes=serializer.validated_data.get("notes", ""),
            terms_and_conditions=serializer.validated_data.get("terms_and_conditions", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            user=self.request.user,
        )
        serializer.instance = po

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request: Request, pk: str = None) -> Response:
        """Submit a DRAFT Purchase Order for approval."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        sub_po = self.po_service.submit_purchase_order(tenant, po, user=request.user)
        return Response(self.get_serializer(sub_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        """Approve a pending Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        app_po = self.po_service.approve_purchase_order(tenant, po, user=request.user)
        return Response(self.get_serializer(app_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request: Request, pk: str = None) -> Response:
        """Reject a pending Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        rej_po = self.po_service.reject_purchase_order(tenant, po, user=request.user)
        return Response(self.get_serializer(rej_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request: Request, pk: str = None) -> Response:
        """Mark Purchase Order as sent to supplier."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        sent_po = self.po_service.send_to_supplier(tenant, po, user=request.user)
        return Response(self.get_serializer(sent_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request: Request, pk: str = None) -> Response:
        """Record supplier acknowledgment of Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        ack_po = self.po_service.acknowledge_order(tenant, po, user=request.user)
        return Response(self.get_serializer(ack_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request: Request, pk: str = None) -> Response:
        """Cancel an un-received Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PurchaseOrderCancelRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        can_po = self.po_service.cancel_purchase_order(tenant, po, reason=serializer.validated_data["reason"], user=request.user)
        return Response(self.get_serializer(can_po).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="amend")
    def amend(self, request: Request, pk: str = None) -> Response:
        """Create a controlled amendment for an approved Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PurchaseOrderAmendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amendment = self.po_service.amend_purchase_order(
            tenant=tenant,
            po=po,
            reason=serializer.validated_data["reason"],
            changes=serializer.validated_data["changes"],
            user=request.user,
        )
        return Response({"amendment_number": amendment.amendment_number, "status": amendment.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request: Request, pk: str = None) -> Response:
        """Close an open or partially received Purchase Order."""
        tenant = getattr(request, "tenant", None)
        po = self.selector.get_purchase_order_by_id(tenant, pk)
        if not po:
            return Response({"detail": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        cls_po = self.po_service.close_purchase_order(tenant, po, user=request.user)
        return Response(self.get_serializer(cls_po).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        """Get operational summary statistics of procurement spend and orders."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_procurement_statistics(tenant, company_id=request.query_params.get("company"))
        return Response(stats, status=status.HTTP_200_OK)

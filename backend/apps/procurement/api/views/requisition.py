"""REST API ViewSet for PurchaseRequisition management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.procurement.api.serializers import PurchaseOrderSerializer, PurchaseRequisitionSerializer
from apps.procurement.selectors import PurchaseRequisitionSelector
from apps.procurement.services import PurchaseOrderService, PurchaseRequisitionService


class PurchaseRequisitionViewSet(viewsets.ModelViewSet):
    """API endpoints for managing Purchase Requisitions, submissions, approvals, and PO conversions."""

    serializer_class = PurchaseRequisitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = PurchaseRequisitionSelector()
        self.requisition_service = PurchaseRequisitionService()
        self.po_service = PurchaseOrderService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_requisitions(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            status=self.request.query_params.get("status"),
            priority=self.request.query_params.get("priority"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        requisition = self.requisition_service.create_requisition(
            tenant=tenant,
            company=serializer.validated_data["company"],
            warehouse=serializer.validated_data["warehouse"],
            lines_data=lines_raw,
            branch=serializer.validated_data.get("branch"),
            department=serializer.validated_data.get("department", ""),
            priority=serializer.validated_data.get("priority"),
            reason=serializer.validated_data.get("reason"),
            required_date=serializer.validated_data.get("required_date"),
            notes=serializer.validated_data.get("notes", ""),
            user=self.request.user,
        )
        serializer.instance = requisition

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request: Request, pk: str = None) -> Response:
        """Submit a DRAFT requisition for approval."""
        tenant = getattr(request, "tenant", None)
        req = self.selector.get_requisition_by_id(tenant, pk)
        if not req:
            return Response({"detail": "Requisition not found."}, status=status.HTTP_404_NOT_FOUND)

        sub_req = self.requisition_service.submit_requisition(tenant, req, user=request.user)
        return Response(self.get_serializer(sub_req).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        """Approve a submitted requisition."""
        tenant = getattr(request, "tenant", None)
        req = self.selector.get_requisition_by_id(tenant, pk)
        if not req:
            return Response({"detail": "Requisition not found."}, status=status.HTTP_404_NOT_FOUND)

        app_req = self.requisition_service.approve_requisition(tenant, req, user=request.user)
        return Response(self.get_serializer(app_req).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request: Request, pk: str = None) -> Response:
        """Reject a submitted requisition."""
        tenant = getattr(request, "tenant", None)
        req = self.selector.get_requisition_by_id(tenant, pk)
        if not req:
            return Response({"detail": "Requisition not found."}, status=status.HTTP_404_NOT_FOUND)

        rej_reason = request.data.get("rejection_reason", "")
        rej_req = self.requisition_service.reject_requisition(tenant, req, rejection_reason=rej_reason, user=request.user)
        return Response(self.get_serializer(rej_req).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="convert-to-po")
    def convert_to_po(self, request: Request, pk: str = None) -> Response:
        """Convert an approved requisition into Purchase Order(s)."""
        tenant = getattr(request, "tenant", None)
        req = self.selector.get_requisition_by_id(tenant, pk)
        if not req:
            return Response({"detail": "Requisition not found."}, status=status.HTTP_404_NOT_FOUND)

        created_pos = self.po_service.convert_requisition_to_purchase_order(tenant, req, user=request.user)
        serializer = PurchaseOrderSerializer(created_pos, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

"""REST API ViewSet for GoodsReceipt management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.goods_receipt.api.serializers import GoodsReceiptReverseRequestSerializer, GoodsReceiptSerializer
from apps.goods_receipt.selectors import GoodsReceiptSelector
from apps.goods_receipt.services import GoodsReceiptService


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    """API endpoints for Goods Receipts, receiving workflow, quality checks, posting, and reversals."""

    serializer_class = GoodsReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = GoodsReceiptSelector()
        self.receipt_service = GoodsReceiptService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_goods_receipts(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            supplier_id=self.request.query_params.get("supplier"),
            purchase_order_id=self.request.query_params.get("purchase_order"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_number=self.request.query_params.get("batch_number"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        receipt = self.receipt_service.create_goods_receipt(
            tenant=tenant,
            company=serializer.validated_data["company"],
            supplier=serializer.validated_data["supplier"],
            warehouse=serializer.validated_data["warehouse"],
            lines_data=lines_raw,
            branch=serializer.validated_data.get("branch"),
            purchase_order=serializer.validated_data.get("purchase_order"),
            receiving_location=serializer.validated_data.get("receiving_location"),
            receipt_date=serializer.validated_data.get("receipt_date"),
            supplier_delivery_number=serializer.validated_data.get("supplier_delivery_number", ""),
            supplier_invoice_reference=serializer.validated_data.get("supplier_invoice_reference", ""),
            currency=serializer.validated_data.get("currency", "USD"),
            exchange_rate=serializer.validated_data.get("exchange_rate", "1.000000"),
            shipping_cost=serializer.validated_data.get("shipping_cost", "0.0000"),
            other_charges=serializer.validated_data.get("other_charges", "0.0000"),
            notes=serializer.validated_data.get("notes", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            user=self.request.user,
        )
        serializer.instance = receipt

    @action(detail=True, methods=["post"], url_path="post")
    def post_receipt(self, request: Request, pk: str = None) -> Response:
        """POSTING ENGINE: Post physical stock to inventory via StockMovementEngine and update PO counters."""
        tenant = getattr(request, "tenant", None)
        receipt = self.selector.get_goods_receipt_by_id(tenant, pk)
        if not receipt:
            return Response({"detail": "Goods Receipt not found."}, status=status.HTTP_404_NOT_FOUND)

        posted_receipt = self.receipt_service.post_goods_receipt(tenant, receipt, user=request.user)
        return Response(self.get_serializer(posted_receipt).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse_receipt(self, request: Request, pk: str = None) -> Response:
        """Create a compensating inventory reversal and update PO counters."""
        tenant = getattr(request, "tenant", None)
        receipt = self.selector.get_goods_receipt_by_id(tenant, pk)
        if not receipt:
            return Response({"detail": "Goods Receipt not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GoodsReceiptReverseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reversed_receipt = self.receipt_service.reverse_goods_receipt(
            tenant, receipt, reason=serializer.validated_data["reason"], user=request.user
        )
        return Response(self.get_serializer(reversed_receipt).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        """Get receiving statistics summary."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_receiving_statistics(tenant, company_id=request.query_params.get("company"))
        return Response(stats, status=status.HTTP_200_OK)

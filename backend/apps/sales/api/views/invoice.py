"""REST API ViewSets for SalesInvoice and POS counter operations."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.medicines.serializers.medicine import MedicineSerializer
from apps.sales.api.serializers import SalesInvoiceSerializer
from apps.sales.selectors import PosSelector
from apps.sales.services import PosSalesService


class SalesInvoiceViewSet(viewsets.ModelViewSet):
    """API endpoints for SalesInvoices, POS sales, voiding, payments, and analytics."""

    serializer_class = SalesInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = PosSelector()
        self.sales_service = PosSalesService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_sales_invoices(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            warehouse_id=self.request.query_params.get("warehouse"),
            customer_id=self.request.query_params.get("customer"),
            cashier_id=self.request.query_params.get("cashier"),
            status=self.request.query_params.get("status"),
            payment_status=self.request.query_params.get("payment_status"),
            date_from=self.request.query_params.get("date_from"),
            date_to=self.request.query_params.get("date_to"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        invoice = self.sales_service.create_draft_or_held_sale(
            tenant=tenant,
            company=serializer.validated_data["company"],
            branch=serializer.validated_data["branch"],
            warehouse=serializer.validated_data["warehouse"],
            lines_data=lines_raw,
            customer=serializer.validated_data.get("customer"),
            register_session=serializer.validated_data.get("register_session"),
            status=serializer.validated_data.get("status", "draft"),
            currency=serializer.validated_data.get("currency", "USD"),
            exchange_rate=serializer.validated_data.get("exchange_rate", "1.000000"),
            discount=serializer.validated_data.get("discount", "0.0000"),
            tax=serializer.validated_data.get("tax", "0.0000"),
            other_charges=serializer.validated_data.get("other_charges", "0.0000"),
            notes=serializer.validated_data.get("notes", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            cashier=self.request.user,
            salesperson=serializer.validated_data.get("salesperson"),
        )
        serializer.instance = invoice

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_sale(self, request: Request, pk: str = None) -> Response:
        """POS SALE ENGINE: Atomic stock reduction via StockMovementEngine and payment processing."""
        tenant = getattr(request, "tenant", None)
        inv = self.get_queryset().filter(pk=pk).first()
        if not inv:
            return Response({"detail": "Sales Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        payments_raw = request.data.get("payments", [])
        comp_inv = self.sales_service.complete_sale(tenant, inv, payments_data=payments_raw, user=request.user)
        return Response(self.get_serializer(comp_inv).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="void")
    def void_sale(self, request: Request, pk: str = None) -> Response:
        """Void a completed sale, restoring physical inventory via compensating StockMovementEngine movements."""
        tenant = getattr(request, "tenant", None)
        inv = self.get_queryset().filter(pk=pk).first()
        if not inv:
            return Response({"detail": "Sales Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get("reason", "")
        void_inv = self.sales_service.void_completed_sale(tenant, inv, reason=reason, user=request.user)
        return Response(self.get_serializer(void_inv).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="lookup/barcode")
    def barcode_lookup(self, request: Request) -> Response:
        """Fast POS lookup for medicines by barcode, SKU, or name."""
        tenant = getattr(request, "tenant", None)
        query = request.query_params.get("q", "")
        if not query:
            return Response([], status=status.HTTP_200_OK)

        meds = self.selector.barcode_or_sku_lookup(tenant, query)
        return Response(MedicineSerializer(meds, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="analytics")
    def analytics(self, request: Request) -> Response:
        """Get gross sales, gross profit, and payment method statistics."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_sales_analytics(
            tenant=tenant,
            company_id=request.query_params.get("company"),
            branch_id=request.query_params.get("branch"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        return Response(stats, status=status.HTTP_200_OK)

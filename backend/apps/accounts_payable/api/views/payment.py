"""REST API ViewSet for SupplierPayment management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_payable.api.serializers import SupplierPaymentSerializer
from apps.accounts_payable.selectors import AccountsPayableSelector
from apps.accounts_payable.services import AccountsPayableService


class SupplierPaymentViewSet(viewsets.ModelViewSet):
    """API endpoints for processing supplier payments, status tracking, and reversals."""

    serializer_class = SupplierPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = AccountsPayableSelector()
        self.ap_service = AccountsPayableService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        qs = self.ap_service.payment_repository.get_queryset(tenant).select_related("company", "branch", "supplier", "supplier_invoice", "created_by")
        supplier_id = self.request.query_params.get("supplier")
        invoice_id = self.request.query_params.get("supplier_invoice")
        status_param = self.request.query_params.get("status")

        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if invoice_id:
            qs = qs.filter(supplier_invoice_id=invoice_id)
        if status_param:
            qs = qs.filter(status=status_param)

        return qs

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        invoice = serializer.validated_data["supplier_invoice"]
        amount = serializer.validated_data["amount"]

        payment = self.ap_service.process_supplier_payment(
            tenant=tenant,
            invoice=invoice,
            amount=amount,
            payment_date=serializer.validated_data.get("payment_date"),
            payment_method=serializer.validated_data.get("payment_method", "bank_transfer"),
            reference_number=serializer.validated_data.get("reference_number", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            notes=serializer.validated_data.get("notes", ""),
            user=self.request.user,
        )
        serializer.instance = payment

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        """Reverse a posted supplier payment, restoring outstanding AP balances."""
        tenant = getattr(request, "tenant", None)
        pmt = self.get_queryset().filter(pk=pk).first()
        if not pmt:
            return Response({"detail": "Supplier Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get("reason", "")
        rev_pmt = self.ap_service.reverse_supplier_payment(tenant, pmt, reason=reason, user=request.user)
        return Response(self.get_serializer(rev_pmt).data, status=status.HTTP_200_OK)

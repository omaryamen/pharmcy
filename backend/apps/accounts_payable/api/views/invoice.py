"""REST API ViewSets for SupplierInvoice and AccountsPayableEntry management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_payable.api.serializers import (
    AccountsPayableEntrySerializer,
    SupplierInvoiceSerializer,
)
from apps.accounts_payable.selectors import AccountsPayableSelector
from apps.accounts_payable.services import AccountsPayableService
from apps.purchase_returns.repositories import SupplierCreditNoteRepository


class SupplierInvoiceViewSet(viewsets.ModelViewSet):
    """API endpoints for SupplierInvoices, 3-way matching, approval, AP posting, credit applications, and payments."""

    serializer_class = SupplierInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = AccountsPayableSelector()
        self.ap_service = AccountsPayableService()
        self.crn_repository = SupplierCreditNoteRepository()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_supplier_invoices(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            supplier_id=self.request.query_params.get("supplier"),
            purchase_order_id=self.request.query_params.get("purchase_order"),
            goods_receipt_id=self.request.query_params.get("goods_receipt"),
            status=self.request.query_params.get("status"),
            match_status=self.request.query_params.get("match_status"),
            due_date_before=self.request.query_params.get("due_date_before"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        lines_raw = self.request.data.get("lines", [])
        invoice = self.ap_service.create_supplier_invoice(
            tenant=tenant,
            company=serializer.validated_data["company"],
            supplier=serializer.validated_data["supplier"],
            supplier_invoice_number=serializer.validated_data["supplier_invoice_number"],
            invoice_date=serializer.validated_data["invoice_date"],
            lines_data=lines_raw,
            branch=serializer.validated_data.get("branch"),
            purchase_order=serializer.validated_data.get("purchase_order"),
            goods_receipt=serializer.validated_data.get("goods_receipt"),
            payment_terms=serializer.validated_data.get("payment_terms", "net_30"),
            custom_due_date=serializer.validated_data.get("due_date"),
            currency=serializer.validated_data.get("currency", "USD"),
            exchange_rate=serializer.validated_data.get("exchange_rate", "1.000000"),
            discount=serializer.validated_data.get("discount", "0.0000"),
            tax=serializer.validated_data.get("tax", "0.0000"),
            shipping=serializer.validated_data.get("shipping", "0.0000"),
            other_charges=serializer.validated_data.get("other_charges", "0.0000"),
            notes=serializer.validated_data.get("notes", ""),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            user=self.request.user,
        )
        serializer.instance = invoice

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request: Request, pk: str = None) -> Response:
        """Run 3-way matching logic against PO and Goods Receipt."""
        tenant = getattr(request, "tenant", None)
        inv = self.selector.get_supplier_invoice_by_id(tenant, pk)
        if not inv:
            return Response({"detail": "Supplier Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        verified = self.ap_service.verify_and_match_supplier_invoice(tenant, inv, user=request.user)
        return Response(self.get_serializer(verified).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        """Approve supplier invoice, enforcing separation of duties."""
        tenant = getattr(request, "tenant", None)
        inv = self.selector.get_supplier_invoice_by_id(tenant, pk)
        if not inv:
            return Response({"detail": "Supplier Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = self.ap_service.approve_supplier_invoice(tenant, inv, user=request.user)
        return Response(self.get_serializer(approved).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="post")
    def post_to_ap(self, request: Request, pk: str = None) -> Response:
        """Post approved invoice to Accounts Payable subledger."""
        tenant = getattr(request, "tenant", None)
        inv = self.selector.get_supplier_invoice_by_id(tenant, pk)
        if not inv:
            return Response({"detail": "Supplier Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        ap_entry = self.ap_service.post_supplier_invoice(tenant, inv, user=request.user)
        return Response(AccountsPayableEntrySerializer(ap_entry).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="apply-credit")
    def apply_credit(self, request: Request, pk: str = None) -> Response:
        """Apply a Supplier Credit Note against an open posted invoice."""
        tenant = getattr(request, "tenant", None)
        inv = self.selector.get_supplier_invoice_by_id(tenant, pk)
        if not inv:
            return Response({"detail": "Supplier Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        crn_id = request.data.get("credit_note_id")
        amount = request.data.get("amount")

        from apps.purchase_returns.models import SupplierCreditNote
        crn = SupplierCreditNote.objects.filter(tenant=tenant, pk=crn_id).first()
        if not crn:
            return Response({"detail": "Supplier Credit Note not found."}, status=status.HTTP_404_NOT_FOUND)

        app_rec = self.ap_service.apply_supplier_credit(tenant, crn, inv, amount, user=request.user)
        return Response({"detail": f"Successfully applied credit {crn.credit_note_number} ({app_rec.applied_amount})."}, status=status.HTTP_200_OK)


class AccountsPayableViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for viewing Accounts Payable entries, aging, and supplier balances."""

    serializer_class = AccountsPayableEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = AccountsPayableSelector()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_accounts_payable_entries(
            tenant=tenant,
            supplier_id=self.request.query_params.get("supplier"),
            status=self.request.query_params.get("status"),
        )

    @action(detail=False, methods=["get"], url_path="aging")
    def aging(self, request: Request) -> Response:
        """Get Accounts Payable aging report breakdown."""
        tenant = getattr(request, "tenant", None)
        aging = self.selector.calculate_ap_aging(tenant, supplier_id=request.query_params.get("supplier"))
        return Response(aging, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        """Get total purchases, payments, credits, and outstanding AP balance statistics."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_supplier_balance_summary(tenant, supplier_id=request.query_params.get("supplier"))
        return Response(stats, status=status.HTTP_200_OK)

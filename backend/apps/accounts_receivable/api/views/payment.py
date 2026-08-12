"""REST API ViewSet for CustomerPayment posting, allocation, and reversals."""

from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_receivable.api.serializers import (
    CustomerPaymentSerializer,
    PostPaymentSerializer,
    ReversePaymentSerializer,
)
from apps.accounts_receivable.models import CustomerPayment
from apps.accounts_receivable.selectors import ReceivableSelector
from apps.accounts_receivable.services import CustomerPaymentService
from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer


class CustomerPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet managing CustomerPayment posting, multi-receivable allocation, and reversals."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerPaymentSerializer
    selector = ReceivableSelector()
    service = CustomerPaymentService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_payments(
            tenant=tenant,
            customer_id=self.request.query_params.get("customer_id"),
            status=self.request.query_params.get("status"),
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PostPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        customer = Customer.objects.get(pk=data["customer_id"], tenant=tenant)
        branch = Branch.objects.get(pk=data["branch_id"], tenant=tenant) if data.get("branch_id") else None

        payment = self.service.post_customer_payment(
            tenant=tenant,
            company=company,
            customer=customer,
            amount=data["amount"],
            payment_method=data.get("payment_method", "cash"),
            allocations_data=data.get("allocations", []),
            branch=branch,
            reference_number=data.get("reference_number", ""),
            overpayment_policy=data.get("overpayment_policy", "allow_as_customer_credit"),
            idempotency_key=data.get("idempotency_key", ""),
            user=request.user,
            notes=data.get("notes", ""),
        )
        return Response(CustomerPaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        serializer = ReversePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = getattr(request.user, "tenant", None)
        pmt = self.get_object()

        reversed_pmt = self.service.reverse_customer_payment(
            tenant=tenant,
            payment=pmt,
            reversal_reason=serializer.validated_data["reversal_reason"],
            user=request.user,
        )
        return Response(CustomerPaymentSerializer(reversed_pmt).data, status=status.HTTP_200_OK)

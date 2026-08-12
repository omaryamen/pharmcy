"""REST API ViewSet for BankReconciliation and matching."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cash_and_bank.api.serializers import (
    BankReconciliationSerializer,
    MatchTransactionSerializer,
    ReconciliationMatchSerializer,
)
from apps.cash_and_bank.models import BankReconciliation, BankTransaction
from apps.cash_and_bank.services import FinancialReconciliationService


class BankReconciliationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BankReconciliationSerializer
    service = FinancialReconciliationService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return BankReconciliation.objects.filter(tenant=tenant)

    @action(detail=True, methods=["post"], url_path="match")
    def match_transaction(self, request: Request, pk: str = None) -> Response:
        serializer = MatchTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        rec = self.get_object()
        btx = BankTransaction.objects.get(pk=data["bank_transaction_id"], tenant=tenant)

        match = self.service.match_transaction(
            tenant=tenant,
            reconciliation=rec,
            bank_transaction=btx,
            reference_type=data["reference_type"],
            reference_id=data["reference_id"],
            matched_amount=data["matched_amount"],
        )
        return Response(ReconciliationMatchSerializer(match).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        rec = self.get_object()

        approved_rec = self.service.approve_reconciliation(tenant, rec, approver=request.user)
        return Response(BankReconciliationSerializer(approved_rec).data, status=status.HTTP_200_OK)

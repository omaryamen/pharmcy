"""REST API ViewSets for CashAccount and BankAccount management."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.cash_and_bank.api.serializers import BankAccountSerializer, CashAccountSerializer
from apps.cash_and_bank.selectors import TreasurySelector


class CashAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CashAccountSerializer
    selector = TreasurySelector()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_cash_accounts(
            tenant=tenant,
            company_id=self.request.query_params.get("company_id"),
            branch_id=self.request.query_params.get("branch_id"),
        )


class BankAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BankAccountSerializer
    selector = TreasurySelector()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_bank_accounts(
            tenant=tenant,
            company_id=self.request.query_params.get("company_id"),
            branch_id=self.request.query_params.get("branch_id"),
        )

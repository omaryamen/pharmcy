"""REST API ViewSet serving Financial Statements & Audit Reconciliation reports."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.companies.models import Company
from apps.general_ledger.api.serializers import (
    BalanceSheetSerializer,
    ProfitAndLossSerializer,
    TrialBalanceSerializer,
)
from apps.general_ledger.selectors import GLSelector
from apps.general_ledger.services import GLReconciliationService


class FinancialReportsViewSet(viewsets.ViewSet):
    """ViewSet serving Trial Balance, Income Statement (P&L), Balance Sheet, and Audit Reconciliation."""

    permission_classes = [IsAuthenticated]
    selector = GLSelector()
    reconciliation_service = GLReconciliationService()

    @action(detail=False, methods=["get"], url_path="trial-balance")
    def trial_balance(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        as_of_date = request.query_params.get("as_of_date")

        tb = self.selector.get_trial_balance(tenant, company_id=company_id, as_of_date=as_of_date)
        return Response(TrialBalanceSerializer(tb).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="profit-loss")
    def profit_loss(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        pnl = self.selector.get_profit_and_loss(tenant, company_id=company_id, start_date=start_date, end_date=end_date)
        return Response(ProfitAndLossSerializer(pnl).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="balance-sheet")
    def balance_sheet(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        as_of_date = request.query_params.get("as_of_date")

        bs = self.selector.get_balance_sheet(tenant, company_id=company_id, as_of_date=as_of_date)
        return Response(BalanceSheetSerializer(bs).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="reconciliation")
    def reconciliation(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        company = Company.objects.get(pk=company_id, tenant=tenant)

        audit = self.reconciliation_service.audit_general_ledger_integrity(tenant, company)
        return Response(audit, status=status.HTTP_200_OK)

"""REST API ViewSet for Authoritative Financial Statements & Subledger Aging."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.reports.selectors import FinancialReportSelector, ReportFilterDTO


class FinancialReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    selector = FinancialReportSelector()

    def _build_filter_dto(self, request: Request) -> ReportFilterDTO:
        tenant = getattr(request.user, "tenant", None)
        return ReportFilterDTO(
            tenant=tenant,
            company_id=request.query_params.get("company_id"),
            period_type=request.query_params.get("period_type"),
        )

    @action(detail=False, methods=["get"], url_path="trial-balance")
    def trial_balance(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_trial_balance(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="profit-and-loss")
    def profit_and_loss(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_profit_and_loss(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="balance-sheet")
    def balance_sheet(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_balance_sheet(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="ar-aging")
    def ar_aging(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_ar_aging(dto)
        return Response(res, status=status.HTTP_200_OK)

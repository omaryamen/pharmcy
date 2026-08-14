"""REST API ViewSet for Sales & POS reports."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.reports.selectors import ReportFilterDTO, SalesReportSelector


class SalesReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    selector = SalesReportSelector()

    def _build_filter_dto(self, request: Request) -> ReportFilterDTO:
        tenant = getattr(request.user, "tenant", None)
        return ReportFilterDTO(
            tenant=tenant,
            company_id=request.query_params.get("company_id"),
            branch_id=request.query_params.get("branch_id"),
            customer_id=request.query_params.get("customer_id"),
            user_id=request.query_params.get("user_id"),
            period_type=request.query_params.get("period_type"),
        )

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_sales_summary(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-branch")
    def by_branch(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_sales_by_branch(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-cashier")
    def by_cashier(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_sales_by_cashier(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="trend")
    def trend(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_sales_trend(dto)
        return Response(res, status=status.HTTP_200_OK)

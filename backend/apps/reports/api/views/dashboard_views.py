"""REST API ViewSet for Executive Management Dashboard & KPI analytics."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.reports.selectors import ExecutiveDashboardSelector, ReportFilterDTO


class ExecutiveDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    selector = ExecutiveDashboardSelector()

    def _build_filter_dto(self, request: Request) -> ReportFilterDTO:
        tenant = getattr(request.user, "tenant", None)
        return ReportFilterDTO(
            tenant=tenant,
            company_id=request.query_params.get("company_id"),
            branch_id=request.query_params.get("branch_id"),
            period_type=request.query_params.get("period_type"),
        )

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_executive_summary(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="charts")
    def charts(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_chart_analytics(dto)
        return Response(res, status=status.HTTP_200_OK)

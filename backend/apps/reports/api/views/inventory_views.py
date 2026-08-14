"""REST API ViewSet for Inventory & Batch reports."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.reports.selectors import InventoryReportSelector, ReportFilterDTO


class InventoryReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    selector = InventoryReportSelector()

    def _build_filter_dto(self, request: Request) -> ReportFilterDTO:
        tenant = getattr(request.user, "tenant", None)
        return ReportFilterDTO(
            tenant=tenant,
            company_id=request.query_params.get("company_id"),
            branch_id=request.query_params.get("branch_id"),
            warehouse_id=request.query_params.get("warehouse_id"),
        )

    @action(detail=False, methods=["get"], url_path="valuation")
    def valuation(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_stock_valuation_summary(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_low_stock_items(dto)
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="expiry-risk")
    def expiry_risk(self, request: Request) -> Response:
        dto = self._build_filter_dto(request)
        res = self.selector.get_expiry_risk_summary(dto)
        return Response(res, status=status.HTTP_200_OK)

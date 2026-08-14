"""REST API ViewSet for Multi-Format Report File Exports (CSV, JSON)."""

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.companies.models import Company
from apps.reports.selectors import ReportFilterDTO, SalesReportSelector
from apps.reports.services import ReportExportService


class ReportExportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    sales_selector = SalesReportSelector()
    export_service = ReportExportService()

    @action(detail=False, methods=["post"], url_path="sales/csv")
    def export_sales_csv(self, request: Request) -> Response | HttpResponse:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.data.get("company_id")
        company = Company.objects.filter(pk=company_id, tenant=tenant).first() if company_id else None

        dto = ReportFilterDTO(
            tenant=tenant,
            company_id=company_id,
            period_type=request.data.get("period_type"),
        )
        sales_trend = self.sales_selector.get_sales_trend(dto)

        csv_str, filename = self.export_service.export_report_to_csv(
            tenant=tenant,
            company=company,
            report_code="RPT-SAL-TREND",
            category="sales",
            data_rows=sales_trend,
            user=request.user,
        )

        response = HttpResponse(csv_str, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

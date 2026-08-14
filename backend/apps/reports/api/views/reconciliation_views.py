"""REST API ViewSet for Platform Financial Reconciliation Audits."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.companies.models import Company
from apps.reports.services import ReportReconciliationService


class ReportReconciliationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    recon_service = ReportReconciliationService()

    @action(detail=False, methods=["get"], url_path="audit")
    def audit(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        company = Company.objects.filter(pk=company_id, tenant=tenant).first() if company_id else Company.objects.filter(tenant=tenant).first()

        if not company:
            return Response({"error": "No valid company context found."}, status=status.HTTP_400_BAD_REQUEST)

        audit_res = self.recon_service.run_platform_reconciliation_audit(tenant, company)
        return Response(audit_res, status=status.HTTP_200_OK)

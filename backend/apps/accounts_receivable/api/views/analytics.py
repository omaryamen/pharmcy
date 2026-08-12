"""REST API ViewSet for AR Aging, Statistics, and Reconciliation reporting."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_receivable.selectors import ReceivableSelector
from apps.accounts_receivable.services import ARReconciliationService
from apps.customers.models import Customer


class ARAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet serving AR aging analysis, subledger statistics, and reconciliation audits."""

    permission_classes = [IsAuthenticated]
    selector = ReceivableSelector()
    reconciliation_service = ARReconciliationService()

    @action(detail=False, methods=["get"], url_path="aging")
    def aging(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")
        customer_id = request.query_params.get("customer_id")

        aging_data = self.selector.get_ar_aging_report(tenant=tenant, company_id=company_id, customer_id=customer_id)
        return Response(aging_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")

        stats = self.selector.get_ar_statistics(tenant=tenant, company_id=company_id)
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="reconciliation/(?P<customer_id>[^/.]+)")
    def reconciliation(self, request: Request, customer_id: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        customer = Customer.objects.get(pk=customer_id, tenant=tenant)

        audit = self.reconciliation_service.reconcile_customer_balance(tenant=tenant, customer=customer)
        return Response(audit, status=status.HTTP_200_OK)

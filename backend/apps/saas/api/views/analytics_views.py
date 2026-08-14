"""REST API View for SaaS Revenue Analytics (MRR, ARR, Churn)."""

from rest_framework import status, views
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.saas.selectors import SaaSAnalyticsSelector


class SaaSAnalyticsView(views.APIView):
    permission_classes = [IsAdminUser]
    selector = SaaSAnalyticsSelector()

    def get(self, request: Request) -> Response:
        currency = request.query_params.get("currency", "USD")
        metrics = self.selector.get_saas_metrics_summary(currency=currency)
        return Response(metrics, status=status.HTTP_200_OK)

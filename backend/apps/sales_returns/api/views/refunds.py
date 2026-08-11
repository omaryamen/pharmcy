"""REST API ViewSet for Customer Refund transactions."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.sales_returns.api.serializers import CustomerRefundSerializer
from apps.sales_returns.models import CustomerRefund
from apps.sales_returns.selectors import ReturnsSelector


class CustomerRefundViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for inspecting Customer Refund payment transactions."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerRefundSerializer
    selector = ReturnsSelector()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_customer_refunds(
            tenant=tenant,
            customer_id=self.request.query_params.get("customer_id"),
            status=self.request.query_params.get("status"),
        )

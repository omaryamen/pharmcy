"""REST API ViewSet for Customer Financial Statement generation."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts_receivable.api.serializers import CustomerStatementSerializer
from apps.accounts_receivable.selectors import ReceivableSelector


class CustomerStatementViewSet(viewsets.ViewSet):
    """ViewSet serving Customer Statements and running balance ledgers."""

    permission_classes = [IsAuthenticated]
    selector = ReceivableSelector()

    @action(detail=False, methods=["get"], url_path="(?P<customer_id>[^/.]+)")
    def get_statement(self, request: Request, customer_id: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        statement_data = self.selector.get_customer_statement(
            tenant=tenant,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
        )
        return Response(CustomerStatementSerializer(statement_data).data, status=status.HTTP_200_OK)

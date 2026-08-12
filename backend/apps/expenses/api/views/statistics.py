"""REST API ViewSet for Expense statistics and executive summary reporting."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.expenses.selectors import ExpenseSelector


class ExpenseStatisticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    selector = ExpenseSelector()

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        company_id = request.query_params.get("company_id")

        summary = self.selector.get_expense_summary(tenant, company_id=company_id)
        return Response(summary, status=status.HTTP_200_OK)

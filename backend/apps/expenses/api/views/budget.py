"""REST API ViewSet for ExpenseBudget management."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.expenses.api.serializers import ExpenseBudgetSerializer
from apps.expenses.models import ExpenseBudget


class ExpenseBudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseBudgetSerializer

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return ExpenseBudget.objects.filter(tenant=tenant)

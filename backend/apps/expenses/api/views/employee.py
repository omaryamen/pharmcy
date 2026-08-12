"""REST API ViewSet for EmployeeExpense claims."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.expenses.api.serializers import EmployeeExpenseSerializer
from apps.expenses.models import EmployeeExpense


class EmployeeExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeExpenseSerializer

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return EmployeeExpense.objects.filter(tenant=tenant)

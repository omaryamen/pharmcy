"""REST API ViewSet for ExpenseCategory management."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.expenses.api.serializers import ExpenseCategorySerializer
from apps.expenses.models import ExpenseCategory
from apps.expenses.services import ExpenseNumberGenerator


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseCategorySerializer
    number_generator = ExpenseNumberGenerator()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return ExpenseCategory.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, "tenant", None)
        code = self.number_generator.generate_category_code(tenant)
        serializer.save(tenant=tenant, code=code, created_by=self.request.user)

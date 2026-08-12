"""REST API serializer for ExpenseBudget."""

from rest_framework import serializers

from apps.expenses.models import ExpenseBudget


class ExpenseBudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_amount = serializers.DecimalField(max_digits=14, decimal_places=4, read_only=True)
    utilization_percentage = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = ExpenseBudget
        fields = [
            "id",
            "company",
            "branch",
            "category",
            "category_name",
            "fiscal_year",
            "period_number",
            "department_name",
            "cost_center_code",
            "budget_amount",
            "committed_amount",
            "actual_amount",
            "available_amount",
            "utilization_percentage",
            "currency",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "available_amount", "utilization_percentage", "created_at"]

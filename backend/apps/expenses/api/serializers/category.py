"""REST API serializer for ExpenseCategory."""

from rest_framework import serializers

from apps.expenses.models import ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)

    class Meta:
        model = ExpenseCategory
        fields = [
            "id",
            "code",
            "name",
            "name_ar",
            "name_en",
            "company",
            "company_name",
            "parent",
            "gl_expense_account",
            "tax_account",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]

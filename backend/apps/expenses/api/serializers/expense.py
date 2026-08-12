"""REST API serializers for Expense and ExpenseLine."""

from rest_framework import serializers

from apps.expenses.models import Expense, ExpenseLine


class ExpenseLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseLine
        fields = [
            "id",
            "category",
            "gl_account",
            "description",
            "quantity",
            "unit_cost",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "department_name",
            "cost_center_code",
            "notes",
        ]
        read_only_fields = ["id", "subtotal", "total_amount"]


class ExpenseSerializer(serializers.ModelSerializer):
    lines = ExpenseLineSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "expense_number",
            "company",
            "branch",
            "category",
            "category_name",
            "expense_request",
            "employee",
            "supplier",
            "expense_date",
            "due_date",
            "department_name",
            "cost_center_code",
            "description",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "currency",
            "exchange_rate",
            "base_total_amount",
            "payment_method",
            "payment_status",
            "approval_status",
            "accounting_status",
            "lines",
            "created_at",
        ]
        read_only_fields = ["id", "expense_number", "subtotal", "total_amount", "approval_status", "accounting_status", "created_at"]


class CreateExpenseSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    category_id = serializers.UUIDField()
    expense_date = serializers.DateField()
    description = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=4)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=4, default=0)
    payment_method = serializers.CharField(default="cash")
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    employee_id = serializers.UUIDField(required=False, allow_null=True)

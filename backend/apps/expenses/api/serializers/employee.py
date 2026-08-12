"""REST API serializer for EmployeeExpense claims."""

from rest_framework import serializers

from apps.expenses.models import EmployeeExpense


class EmployeeExpenseSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)

    class Meta:
        model = EmployeeExpense
        fields = [
            "id",
            "claim_number",
            "company",
            "employee",
            "employee_name",
            "expense",
            "claim_amount",
            "approved_amount",
            "reimbursed_amount",
            "remaining_amount",
            "status",
            "payment_reference",
            "reimbursed_at",
            "created_at",
        ]
        read_only_fields = ["id", "claim_number", "status", "created_at"]

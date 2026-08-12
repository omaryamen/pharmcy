"""REST API serializer for ExpenseRequest."""

from rest_framework import serializers

from apps.expenses.models import ExpenseRequest


class ExpenseRequestSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    requester_name = serializers.CharField(source="requester.get_full_name", read_only=True)

    class Meta:
        model = ExpenseRequest
        fields = [
            "id",
            "request_number",
            "company",
            "branch",
            "category",
            "category_name",
            "requester",
            "requester_name",
            "department_name",
            "cost_center_code",
            "estimated_amount",
            "currency",
            "purpose",
            "business_justification",
            "required_date",
            "status",
            "approved_by",
            "rejected_by",
            "approval_notes",
            "created_at",
        ]
        read_only_fields = ["id", "request_number", "status", "created_at"]

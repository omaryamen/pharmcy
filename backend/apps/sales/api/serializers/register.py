"""REST API serializers for CashRegister and RegisterSession entities."""

from rest_framework import serializers

from apps.sales.models import CashRegister, RegisterSession


class CashRegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")

    class Meta:
        model = CashRegister
        fields = [
            "id",
            "register_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "warehouse",
            "warehouse_name",
            "name",
            "status",
            "opening_balance",
            "current_balance",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "register_number", "status", "created_at", "updated_at"]


class RegisterSessionSerializer(serializers.ModelSerializer):
    cash_register_name = serializers.ReadOnlyField(source="cash_register.name")
    cashier_name = serializers.ReadOnlyField(source="cashier.get_full_name")

    class Meta:
        model = RegisterSession
        fields = [
            "id",
            "session_number",
            "cash_register",
            "cash_register_name",
            "cashier",
            "cashier_name",
            "opening_cash",
            "cash_sales",
            "cash_refunds",
            "cash_adjustments",
            "expected_cash",
            "actual_cash",
            "variance",
            "status",
            "opened_at",
            "closed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "session_number",
            "cash_sales",
            "cash_refunds",
            "expected_cash",
            "variance",
            "status",
            "opened_at",
            "closed_at",
            "created_at",
        ]

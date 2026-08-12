"""REST API serializers for CashAccount and BankAccount."""

from rest_framework import serializers

from apps.cash_and_bank.models import BankAccount, CashAccount


class CashAccountSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)

    class Meta:
        model = CashAccount
        fields = [
            "id",
            "account_number",
            "name",
            "company",
            "company_name",
            "branch",
            "gl_account",
            "currency",
            "status",
            "opening_balance",
            "current_balance",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "bank_name",
            "account_name",
            "account_number",
            "masked_account_number",
            "iban",
            "swift_bic",
            "company",
            "company_name",
            "branch",
            "gl_account",
            "currency",
            "status",
            "opening_balance",
            "current_balance",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

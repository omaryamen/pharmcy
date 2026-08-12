"""REST API serializers for BankTransaction import and listing."""

from rest_framework import serializers

from apps.cash_and_bank.models import BankTransaction


class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = [
            "id",
            "transaction_number",
            "bank_account",
            "external_id",
            "transaction_date",
            "value_date",
            "transaction_type",
            "amount",
            "currency",
            "reference",
            "description",
            "reconciliation_status",
            "imported_at",
        ]
        read_only_fields = ["id", "transaction_number", "imported_at"]


class BankStatementLineInputSerializer(serializers.Serializer):
    transaction_date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    reference = serializers.CharField(required=False, allow_blank=True, default="")
    external_id = serializers.CharField(required=False, allow_blank=True, default="")
    transaction_type = serializers.CharField(required=False, default="deposit")
    description = serializers.CharField(required=False, allow_blank=True, default="")


class ImportBankStatementSerializer(serializers.Serializer):
    bank_account_id = serializers.UUIDField()
    statement_lines = BankStatementLineInputSerializer(many=True)

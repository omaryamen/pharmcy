"""REST API serializers for BankReconciliation and matching."""

from rest_framework import serializers

from apps.cash_and_bank.models import BankReconciliation, ReconciliationMatch


class ReconciliationMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationMatch
        fields = [
            "id",
            "reconciliation",
            "bank_transaction",
            "matched_amount",
            "reference_type",
            "reference_id",
            "is_auto_matched",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BankReconciliationSerializer(serializers.ModelSerializer):
    matches = ReconciliationMatchSerializer(many=True, read_only=True)

    class Meta:
        model = BankReconciliation
        fields = [
            "id",
            "reconciliation_number",
            "company",
            "bank_account",
            "start_date",
            "end_date",
            "opening_balance",
            "statement_closing_balance",
            "book_closing_balance",
            "difference",
            "status",
            "approved_by",
            "reconciled_at",
            "matches",
            "created_at",
        ]
        read_only_fields = ["id", "reconciliation_number", "status", "created_at"]


class MatchTransactionSerializer(serializers.Serializer):
    bank_transaction_id = serializers.UUIDField()
    reference_type = serializers.CharField()
    reference_id = serializers.CharField()
    matched_amount = serializers.DecimalField(max_digits=14, decimal_places=4)

"""REST API serializers for Cash deposits, withdrawals, and transfers."""

from rest_framework import serializers

from apps.cash_and_bank.models import CashDeposit, CashTransfer, CashWithdrawal


class CashDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashDeposit
        fields = [
            "id",
            "deposit_number",
            "company",
            "cash_account",
            "bank_account",
            "deposit_date",
            "amount",
            "currency",
            "reference",
            "status",
            "posted_at",
            "created_at",
        ]
        read_only_fields = ["id", "deposit_number", "status", "created_at"]


class CreateDepositSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    cash_account_id = serializers.UUIDField()
    bank_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    reference = serializers.CharField(required=False, allow_blank=True, default="")


class CashWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashWithdrawal
        fields = [
            "id",
            "withdrawal_number",
            "company",
            "bank_account",
            "cash_account",
            "withdrawal_date",
            "amount",
            "currency",
            "purpose",
            "reference",
            "status",
            "posted_at",
            "created_at",
        ]
        read_only_fields = ["id", "withdrawal_number", "status", "created_at"]


class CreateWithdrawalSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    bank_account_id = serializers.UUIDField()
    cash_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    purpose = serializers.CharField(required=False, allow_blank=True, default="")
    reference = serializers.CharField(required=False, allow_blank=True, default="")


class CashTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransfer
        fields = [
            "id",
            "transfer_number",
            "company",
            "source_cash_account",
            "destination_cash_account",
            "transfer_date",
            "amount",
            "currency",
            "reference",
            "status",
            "posted_at",
            "created_at",
        ]
        read_only_fields = ["id", "transfer_number", "status", "created_at"]

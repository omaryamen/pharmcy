"""REST API serializers for JournalEntry and lines."""

from rest_framework import serializers

from apps.general_ledger.models import JournalEntry, JournalEntryLine


class JournalEntryLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.account_code", read_only=True)
    account_name = serializers.CharField(source="account.account_name", read_only=True)

    class Meta:
        model = JournalEntryLine
        fields = [
            "id",
            "account",
            "account_code",
            "account_name",
            "description",
            "debit",
            "credit",
            "currency",
            "exchange_rate",
            "base_debit",
            "base_credit",
            "branch",
        ]
        read_only_fields = ["id"]


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "journal_number",
            "company",
            "branch",
            "accounting_period",
            "journal_date",
            "posting_date",
            "reference_type",
            "reference_id",
            "reference_number",
            "source_module",
            "description",
            "status",
            "total_debit",
            "total_credit",
            "is_balanced",
            "posted_at",
            "posted_by",
            "lines",
            "created_at",
        ]
        read_only_fields = ["id", "journal_number", "status", "total_debit", "total_credit", "is_balanced", "created_at"]


class JournalLineInputSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    debit = serializers.DecimalField(max_digits=14, decimal_places=4, default=0)
    credit = serializers.DecimalField(max_digits=14, decimal_places=4, default=0)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class CreateManualJournalSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    posting_date = serializers.DateField()
    description = serializers.CharField()
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    lines = JournalLineInputSerializer(many=True)


class ReverseJournalSerializer(serializers.Serializer):
    reversal_reason = serializers.CharField()

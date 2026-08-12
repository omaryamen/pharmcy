"""REST API serializers for ChartOfAccount and AccountMapping."""

from rest_framework import serializers

from apps.general_ledger.models import AccountMapping, ChartOfAccount


class ChartOfAccountSerializer(serializers.ModelSerializer):
    parent_code = serializers.CharField(source="parent.account_code", read_only=True, default=None)

    class Meta:
        model = ChartOfAccount
        fields = [
            "id",
            "account_code",
            "account_name",
            "english_name",
            "arabic_name",
            "account_type",
            "account_subtype",
            "parent",
            "parent_code",
            "currency",
            "status",
            "is_system_account",
            "is_control_account",
            "allow_manual_posting",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_system_account", "created_at", "updated_at"]


class AccountMappingSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.account_code", read_only=True)
    account_name = serializers.CharField(source="account.account_name", read_only=True)

    class Meta:
        model = AccountMapping
        fields = ["id", "company", "purpose", "account", "account_code", "account_name", "created_at"]
        read_only_fields = ["id", "created_at"]

"""REST API serializers for AccountingPeriod."""

from rest_framework import serializers

from apps.general_ledger.models import AccountingPeriod


class AccountingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingPeriod
        fields = [
            "id",
            "company",
            "fiscal_year",
            "period_number",
            "name",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ClosePeriodSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")

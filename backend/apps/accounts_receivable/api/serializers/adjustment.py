"""REST API serializers for ReceivableAdjustment."""

from rest_framework import serializers

from apps.accounts_receivable.models import ReceivableAdjustment


class ReceivableAdjustmentSerializer(serializers.ModelSerializer):
    receivable_number = serializers.CharField(source="receivable.receivable_number", read_only=True)

    class Meta:
        model = ReceivableAdjustment
        fields = [
            "id",
            "adjustment_number",
            "company",
            "customer",
            "receivable",
            "receivable_number",
            "adjustment_type",
            "amount",
            "reason",
            "reference",
            "status",
            "approved_by",
            "created_at",
        ]
        read_only_fields = ["id", "adjustment_number", "created_at"]


class CreateAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    adjustment_type = serializers.CharField(required=False, default="credit_adjustment")
    reason = serializers.CharField()
    reference = serializers.CharField(required=False, allow_blank=True, default="")

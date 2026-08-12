"""REST API serializers for ReceivableDispute."""

from rest_framework import serializers

from apps.accounts_receivable.models import ReceivableDispute


class ReceivableDisputeSerializer(serializers.ModelSerializer):
    receivable_number = serializers.CharField(source="receivable.receivable_number", read_only=True)

    class Meta:
        model = ReceivableDispute
        fields = [
            "id",
            "dispute_number",
            "receivable",
            "receivable_number",
            "dispute_amount",
            "reason",
            "status",
            "description",
            "resolution_notes",
            "reviewed_by",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "dispute_number", "created_at"]


class CreateDisputeSerializer(serializers.Serializer):
    dispute_amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    reason = serializers.CharField(required=False, default="wrong_amount")
    description = serializers.CharField()


class ResolveDisputeSerializer(serializers.Serializer):
    resolution_status = serializers.CharField()
    resolution_notes = serializers.CharField()

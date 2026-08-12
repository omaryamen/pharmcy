"""REST API serializers for ReceivableWriteOff."""

from rest_framework import serializers

from apps.accounts_receivable.models import ReceivableWriteOff


class ReceivableWriteOffSerializer(serializers.ModelSerializer):
    receivable_number = serializers.CharField(source="receivable.receivable_number", read_only=True)

    class Meta:
        model = ReceivableWriteOff
        fields = [
            "id",
            "write_off_number",
            "company",
            "customer",
            "receivable",
            "receivable_number",
            "amount",
            "reason",
            "approved_by",
            "created_at",
        ]
        read_only_fields = ["id", "write_off_number", "created_at"]


class CreateWriteOffSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    reason = serializers.CharField()

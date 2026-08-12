"""REST API serializer for Customer Financial Statement."""

from rest_framework import serializers


class StatementEntrySerializer(serializers.Serializer):
    date = serializers.DateField()
    type = serializers.CharField()
    reference = serializers.CharField()
    description = serializers.CharField()
    debit = serializers.DecimalField(max_digits=14, decimal_places=4)
    credit = serializers.DecimalField(max_digits=14, decimal_places=4)
    running_balance = serializers.DecimalField(max_digits=14, decimal_places=4)


class CustomerStatementSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    opening_balance = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_debits = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_credits = serializers.DecimalField(max_digits=14, decimal_places=4)
    closing_balance = serializers.DecimalField(max_digits=14, decimal_places=4)
    statement_entries = StatementEntrySerializer(many=True)

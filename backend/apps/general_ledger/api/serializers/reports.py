"""REST API serializers for Financial Statements & Reports."""

from rest_framework import serializers


class TrialBalanceAccountSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    account_code = serializers.CharField()
    account_name = serializers.CharField()
    account_type = serializers.CharField()
    debit = serializers.DecimalField(max_digits=14, decimal_places=4)
    credit = serializers.DecimalField(max_digits=14, decimal_places=4)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=4)


class TrialBalanceSerializer(serializers.Serializer):
    as_of_date = serializers.DateField()
    total_debit = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_credit = serializers.DecimalField(max_digits=14, decimal_places=4)
    is_balanced = serializers.BooleanField()
    accounts = TrialBalanceAccountSerializer(many=True)


class ProfitAndLossSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_cogs = serializers.DecimalField(max_digits=14, decimal_places=4)
    gross_profit = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=4)
    net_profit = serializers.DecimalField(max_digits=14, decimal_places=4)


class BalanceSheetSerializer(serializers.Serializer):
    as_of_date = serializers.DateField()
    total_assets = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_liabilities = serializers.DecimalField(max_digits=14, decimal_places=4)
    total_equity = serializers.DecimalField(max_digits=14, decimal_places=4)
    is_balanced = serializers.BooleanField()

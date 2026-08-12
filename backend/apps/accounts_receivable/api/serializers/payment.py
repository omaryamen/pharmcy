"""REST API serializers for CustomerPayment and allocations."""

from rest_framework import serializers

from apps.accounts_receivable.models import CustomerPayment, CustomerPaymentAllocation


class CustomerPaymentAllocationSerializer(serializers.ModelSerializer):
    receivable_number = serializers.CharField(source="receivable.receivable_number", read_only=True)

    class Meta:
        model = CustomerPaymentAllocation
        fields = [
            "id",
            "payment",
            "receivable",
            "receivable_number",
            "allocated_amount",
            "allocation_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CustomerPaymentSerializer(serializers.ModelSerializer):
    allocations = CustomerPaymentAllocationSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.english_name", read_only=True)

    class Meta:
        model = CustomerPayment
        fields = [
            "id",
            "payment_number",
            "company",
            "branch",
            "customer",
            "customer_name",
            "payment_date",
            "payment_method",
            "currency",
            "amount",
            "allocated_amount",
            "unallocated_amount",
            "reference_number",
            "status",
            "posted_by",
            "reversed_at",
            "reversal_reason",
            "notes",
            "allocations",
            "created_at",
        ]
        read_only_fields = ["id", "payment_number", "status", "created_at"]


class PaymentAllocationItemSerializer(serializers.Serializer):
    receivable_id = serializers.UUIDField()
    allocated_amount = serializers.DecimalField(max_digits=14, decimal_places=4)


class PostPaymentSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    customer_id = serializers.UUIDField()
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=14, decimal_places=4)
    payment_method = serializers.CharField(required=False, default="cash")
    reference_number = serializers.CharField(required=False, allow_blank=True, default="")
    overpayment_policy = serializers.CharField(required=False, default="allow_as_customer_credit")
    idempotency_key = serializers.CharField(required=False, allow_blank=True, default="")
    allocations = PaymentAllocationItemSerializer(many=True, required=False, default=list)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ReversePaymentSerializer(serializers.Serializer):
    reversal_reason = serializers.CharField()

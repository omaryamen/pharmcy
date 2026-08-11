"""REST API serializers for SupplierPayment and AccountsPayableEntry entities."""

from rest_framework import serializers

from apps.accounts_payable.models import AccountsPayableEntry, SupplierPayment


class AccountsPayableEntrySerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    invoice_number = serializers.ReadOnlyField(source="supplier_invoice.invoice_number")
    supplier_invoice_number = serializers.ReadOnlyField(source="supplier_invoice.supplier_invoice_number")

    class Meta:
        model = AccountsPayableEntry
        fields = [
            "id",
            "payable_number",
            "company",
            "company_name",
            "branch",
            "supplier",
            "supplier_name",
            "supplier_invoice",
            "invoice_number",
            "supplier_invoice_number",
            "original_amount",
            "paid_amount",
            "applied_credit_amount",
            "outstanding_amount",
            "currency",
            "exchange_rate",
            "due_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "payable_number",
            "original_amount",
            "paid_amount",
            "applied_credit_amount",
            "outstanding_amount",
            "status",
            "created_at",
            "updated_at",
        ]


class SupplierPaymentSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    invoice_number = serializers.ReadOnlyField(source="supplier_invoice.invoice_number")
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")

    class Meta:
        model = SupplierPayment
        fields = [
            "id",
            "payment_number",
            "company",
            "company_name",
            "branch",
            "supplier",
            "supplier_name",
            "supplier_invoice",
            "invoice_number",
            "accounts_payable_entry",
            "payment_date",
            "amount",
            "currency",
            "payment_method",
            "reference_number",
            "status",
            "idempotency_key",
            "created_by",
            "created_by_name",
            "approved_by",
            "posted_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "payment_number",
            "status",
            "created_by",
            "approved_by",
            "posted_at",
            "created_at",
            "updated_at",
        ]

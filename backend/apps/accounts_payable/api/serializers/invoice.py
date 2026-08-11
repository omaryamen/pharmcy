"""REST API serializers for SupplierInvoice entities."""

from rest_framework import serializers

from apps.accounts_payable.models import (
    CreditApplication,
    InvoiceDispute,
    SupplierInvoice,
    SupplierInvoiceLine,
)


class SupplierInvoiceLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")

    class Meta:
        model = SupplierInvoiceLine
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "purchase_order_line",
            "goods_receipt_line",
            "description",
            "quantity",
            "unit",
            "unit_price",
            "discount",
            "tax",
            "line_subtotal",
            "line_total",
            "received_quantity",
            "invoiced_quantity",
            "notes",
        ]
        read_only_fields = ["id", "line_subtotal", "line_total", "received_quantity", "invoiced_quantity"]


class CreditApplicationSerializer(serializers.ModelSerializer):
    credit_note_number = serializers.ReadOnlyField(source="supplier_credit_note.credit_note_number")

    class Meta:
        model = CreditApplication
        fields = [
            "id",
            "supplier_credit_note",
            "credit_note_number",
            "supplier_invoice",
            "accounts_payable_entry",
            "applied_amount",
            "currency",
            "applied_at",
            "notes",
        ]
        read_only_fields = ["id", "applied_at"]


class InvoiceDisputeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")

    class Meta:
        model = InvoiceDispute
        fields = [
            "id",
            "supplier_invoice",
            "dispute_number",
            "reason",
            "amount",
            "evidence",
            "status",
            "created_by",
            "created_by_name",
            "resolution",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "dispute_number", "created_at"]


class SupplierInvoiceSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    branch_name = serializers.ReadOnlyField(source="branch.name")
    supplier_name = serializers.ReadOnlyField(source="supplier.legal_name")
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")
    approved_by_name = serializers.ReadOnlyField(source="approved_by.get_full_name")
    lines = SupplierInvoiceLineSerializer(many=True, read_only=True)
    credit_applications = CreditApplicationSerializer(many=True, read_only=True)
    disputes = InvoiceDisputeSerializer(many=True, read_only=True)

    class Meta:
        model = SupplierInvoice
        fields = [
            "id",
            "invoice_number",
            "supplier_invoice_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "supplier",
            "supplier_name",
            "purchase_order",
            "goods_receipt",
            "invoice_date",
            "due_date",
            "payment_terms",
            "status",
            "match_status",
            "currency",
            "exchange_rate",
            "subtotal",
            "discount",
            "tax",
            "shipping",
            "other_charges",
            "grand_total",
            "paid_amount",
            "outstanding_amount",
            "idempotency_key",
            "created_by",
            "created_by_name",
            "verified_by",
            "approved_by",
            "approved_by_name",
            "verified_at",
            "approved_at",
            "posted_at",
            "notes",
            "lines",
            "credit_applications",
            "disputes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "status",
            "match_status",
            "subtotal",
            "grand_total",
            "paid_amount",
            "outstanding_amount",
            "created_by",
            "verified_by",
            "approved_by",
            "verified_at",
            "approved_at",
            "posted_at",
            "created_at",
            "updated_at",
        ]

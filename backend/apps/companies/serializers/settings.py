"""Company Settings serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.companies.models import CompanySettings


class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = [
            "general_settings",
            "financial_settings",
            "inventory_settings",
            "sales_settings",
            "purchase_settings",
            "pos_settings",
            "barcode_settings",
            "receipt_settings",
            "tax_configuration",
            "invoice_numbering",
            "document_prefixes",
            "default_currency",
            "default_language",
            "theme_configuration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

"""Branch Settings serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.branches.models import BranchSettings


class BranchSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchSettings
        fields = [
            "working_hours",
            "business_days",
            "currency_override",
            "receipt_template",
            "invoice_prefix",
            "tax_settings",
            "pos_settings",
            "barcode_settings",
            "inventory_settings",
            "notification_settings",
            "printer_settings",
            "theme_settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

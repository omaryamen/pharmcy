"""Tenant Profile serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.tenants.models import TenantProfile


class TenantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantProfile
        fields = [
            "legal_name",
            "display_name",
            "business_type",
            "tax_number",
            "registration_number",
            "country",
            "city",
            "address",
            "phone",
            "email",
            "website",
            "logo",
            "timezone",
            "language",
            "currency",
            "date_format",
            "time_format",
            "fiscal_year_start_month",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

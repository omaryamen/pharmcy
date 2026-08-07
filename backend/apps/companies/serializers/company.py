"""Company serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.companies.models import Company
from apps.companies.serializers.settings import CompanySettingsSerializer
from apps.companies.validators import validate_company_code, validate_tax_number


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "tenant",
            "legal_name",
            "commercial_name",
            "code",
            "slug",
            "business_type",
            "license_number",
            "tax_number",
            "commercial_registration",
            "vat_registration",
            "country",
            "city",
            "state",
            "postal_code",
            "address",
            "phone",
            "mobile",
            "email",
            "website",
            "logo",
            "primary_color",
            "secondary_color",
            "currency",
            "timezone",
            "language",
            "fiscal_year_start_month",
            "business_hours",
            "status",
            "notes",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "is_deleted", "created_at", "updated_at"]

    def validate_code(self, value: str) -> str:
        return validate_company_code(value)

    def validate_tax_number(self, value: str) -> str:
        return validate_tax_number(value)


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "legal_name",
            "commercial_name",
            "code",
            "slug",
            "business_type",
            "license_number",
            "tax_number",
            "commercial_registration",
            "vat_registration",
            "country",
            "city",
            "state",
            "postal_code",
            "address",
            "phone",
            "mobile",
            "email",
            "website",
            "logo",
            "primary_color",
            "secondary_color",
            "currency",
            "timezone",
            "language",
            "fiscal_year_start_month",
            "business_hours",
            "notes",
        ]


class CompanyDetailSerializer(CompanySerializer):
    settings = CompanySettingsSerializer(read_only=True)

    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ["settings"]


class CompanyCloneSerializer(serializers.Serializer):
    new_legal_name = serializers.CharField(max_length=200)
    new_code = serializers.CharField(max_length=50)
    new_slug = serializers.CharField(max_length=100)

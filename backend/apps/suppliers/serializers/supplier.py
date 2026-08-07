"""Supplier serializers for Enterprise Vendor management."""

from __future__ import annotations

from rest_framework import serializers

from apps.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "company",
            "company_name",
            "code",
            "legal_name",
            "display_name",
            "supplier_type",
            "supplier_category",
            "registration_number",
            "tax_number",
            "vat_number",
            "status",
            "logo",
            "website",
            "description",
            "primary_contact_name",
            "secondary_contact_name",
            "phone",
            "mobile",
            "whatsapp",
            "email",
            "support_email",
            "fax",
            "country",
            "state",
            "city",
            "district",
            "postal_code",
            "street",
            "building",
            "google_maps_url",
            "latitude",
            "longitude",
            "default_currency",
            "payment_terms",
            "credit_limit",
            "opening_balance",
            "current_balance",
            "preferred_payment_method",
            "bank_name",
            "bank_account",
            "iban",
            "swift",
            "tax_category",
            "business_license",
            "commercial_registration",
            "drug_license",
            "license_expiry_date",
            "insurance_info",
            "is_preferred",
            "is_blacklisted",
            "rating",
            "risk_level",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "company",
            "code",
            "legal_name",
            "display_name",
            "supplier_type",
            "supplier_category",
            "registration_number",
            "tax_number",
            "vat_number",
            "logo",
            "website",
            "description",
            "primary_contact_name",
            "secondary_contact_name",
            "phone",
            "mobile",
            "whatsapp",
            "email",
            "support_email",
            "fax",
            "country",
            "state",
            "city",
            "district",
            "postal_code",
            "street",
            "building",
            "google_maps_url",
            "latitude",
            "longitude",
            "default_currency",
            "payment_terms",
            "credit_limit",
            "opening_balance",
            "preferred_payment_method",
            "bank_name",
            "bank_account",
            "iban",
            "swift",
            "tax_category",
            "business_license",
            "commercial_registration",
            "drug_license",
            "license_expiry_date",
            "insurance_info",
            "is_preferred",
            "rating",
            "risk_level",
            "notes",
        ]


class SupplierDetailSerializer(SupplierSerializer):
    pass


class SupplierImportItemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    legal_name = serializers.CharField(max_length=255)
    display_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    supplier_type = serializers.CharField(max_length=40, required=False, default="distributor")
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    country = serializers.CharField(max_length=100, required=False, default="Yemen")
    city = serializers.CharField(max_length=100, required=False, default="Sanaa")


class SupplierImportSerializer(serializers.Serializer):
    items = serializers.ListField(child=SupplierImportItemSerializer())

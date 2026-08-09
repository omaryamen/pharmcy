"""Serializers for Enterprise Customer Entity and lifecycle operations."""

from __future__ import annotations

from rest_framework import serializers

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer
from apps.customers.serializers.address import CustomerAddressSerializer
from apps.customers.serializers.medical_profile import CustomerMedicalProfileSerializer


class CustomerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "tenant",
            "company",
            "preferred_branch",
            "code",
            "customer_number",
            "customer_type",
            "status",
            "first_name",
            "middle_name",
            "last_name",
            "arabic_name",
            "english_name",
            "preferred_name",
            "display_name",
            "gender",
            "date_of_birth",
            "national_id",
            "passport_number",
            "nationality",
            "occupation",
            "profile_photo",
            "phone",
            "secondary_phone",
            "mobile",
            "whatsapp",
            "email",
            "alternative_email",
            "preferred_contact_method",
            "preferred_communication_language",
            "preferred_language",
            "preferred_currency",
            "preferred_payment_method",
            "sms_notifications",
            "email_notifications",
            "whatsapp_notifications",
            "marketing_consent",
            "credit_allowed",
            "credit_limit",
            "payment_terms",
            "opening_balance",
            "current_balance",
            "credit_status",
            "default_payment_method",
            "tax_category",
            "discount_eligibility",
            "discount_percentage",
            "price_list",
            "customer_group",
            "customer_segment",
            "customer_category",
            "loyalty_account_number",
            "loyalty_points_balance",
            "membership_level",
            "membership_number",
            "loyalty_enrollment_date",
            "loyalty_expiration_date",
            "insurance_provider_name",
            "insurance_policy_number",
            "insurance_member_number",
            "insurance_coverage_status",
            "insurance_coverage_start_date",
            "insurance_coverage_end_date",
            "insurance_category",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "display_name", "created_at", "updated_at"]


class CustomerDetailSerializer(CustomerSerializer):
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    medical_profile = CustomerMedicalProfileSerializer(read_only=True)

    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ["addresses", "medical_profile"]


class CustomerCreateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True)
    preferred_branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_blank=True)
    customer_number = serializers.CharField(required=False, allow_blank=True)
    medical_profile_data = serializers.JSONField(required=False, write_only=True)
    addresses_data = serializers.ListField(child=serializers.JSONField(), required=False, write_only=True)

    class Meta:
        model = Customer
        fields = [
            "company",
            "preferred_branch",
            "code",
            "customer_number",
            "customer_type",
            "first_name",
            "middle_name",
            "last_name",
            "arabic_name",
            "english_name",
            "preferred_name",
            "gender",
            "date_of_birth",
            "national_id",
            "passport_number",
            "nationality",
            "occupation",
            "profile_photo",
            "phone",
            "secondary_phone",
            "mobile",
            "whatsapp",
            "email",
            "alternative_email",
            "preferred_contact_method",
            "preferred_communication_language",
            "preferred_language",
            "preferred_currency",
            "preferred_payment_method",
            "sms_notifications",
            "email_notifications",
            "whatsapp_notifications",
            "marketing_consent",
            "notification_preferences",
            "credit_allowed",
            "credit_limit",
            "payment_terms",
            "opening_balance",
            "current_balance",
            "credit_status",
            "default_payment_method",
            "tax_category",
            "discount_eligibility",
            "discount_percentage",
            "price_list",
            "customer_group",
            "customer_segment",
            "customer_category",
            "loyalty_account_number",
            "loyalty_points_balance",
            "membership_level",
            "membership_number",
            "loyalty_enrollment_date",
            "loyalty_expiration_date",
            "insurance_provider_name",
            "insurance_policy_number",
            "insurance_member_number",
            "insurance_coverage_status",
            "insurance_coverage_start_date",
            "insurance_coverage_end_date",
            "insurance_category",
            "notes",
            "medical_profile_data",
            "addresses_data",
        ]


class CustomerUpdateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True)
    preferred_branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Customer
        fields = [
            "company",
            "preferred_branch",
            "customer_type",
            "first_name",
            "middle_name",
            "last_name",
            "arabic_name",
            "english_name",
            "preferred_name",
            "gender",
            "date_of_birth",
            "national_id",
            "passport_number",
            "nationality",
            "occupation",
            "profile_photo",
            "phone",
            "secondary_phone",
            "mobile",
            "whatsapp",
            "email",
            "alternative_email",
            "preferred_contact_method",
            "preferred_communication_language",
            "preferred_language",
            "preferred_currency",
            "preferred_payment_method",
            "sms_notifications",
            "email_notifications",
            "whatsapp_notifications",
            "marketing_consent",
            "notification_preferences",
            "credit_allowed",
            "credit_limit",
            "payment_terms",
            "credit_status",
            "default_payment_method",
            "tax_category",
            "discount_eligibility",
            "discount_percentage",
            "price_list",
            "customer_group",
            "customer_segment",
            "customer_category",
            "loyalty_account_number",
            "loyalty_points_balance",
            "membership_level",
            "membership_number",
            "loyalty_enrollment_date",
            "loyalty_expiration_date",
            "insurance_provider_name",
            "insurance_policy_number",
            "insurance_member_number",
            "insurance_coverage_status",
            "insurance_coverage_start_date",
            "insurance_coverage_end_date",
            "insurance_category",
            "notes",
        ]


class DuplicateCheckRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True, default="")
    mobile = serializers.CharField(required=False, allow_blank=True, default="")
    email = serializers.CharField(required=False, allow_blank=True, default="")
    national_id = serializers.CharField(required=False, allow_blank=True, default="")
    passport_number = serializers.CharField(required=False, allow_blank=True, default="")
    insurance_member_number = serializers.CharField(required=False, allow_blank=True, default="")
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    arabic_name = serializers.CharField(required=False, allow_blank=True, default="")
    english_name = serializers.CharField(required=False, allow_blank=True, default="")
    exclude_customer_id = serializers.UUIDField(required=False, allow_null=True)

"""Serializers for Customer Medical Profile sub-resource."""

from __future__ import annotations

from rest_framework import serializers

from apps.customers.models import CustomerMedicalProfile


class CustomerMedicalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMedicalProfile
        fields = [
            "id",
            "customer",
            "blood_type",
            "allergies",
            "chronic_conditions",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "medical_notes",
            "preferred_physician",
            "preferred_pharmacy",
            "insurance_info_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "customer", "created_at", "updated_at"]

"""Employee Profile serializer."""

from __future__ import annotations

from rest_framework import serializers

from apps.users.models import EmployeeProfile


class EmployeeProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    primary_branch_name = serializers.CharField(source="primary_branch.name", read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            "company",
            "company_name",
            "primary_branch",
            "primary_branch_name",
            "employee_number",
            "arabic_name",
            "english_name",
            "national_id",
            "passport_number",
            "gender",
            "date_of_birth",
            "job_title",
            "department",
            "employment_type",
            "position",
            "job_grade",
            "hire_date",
            "termination_date",
            "manager",
            "direct_supervisor",
            "emergency_contact",
            "mfa_enabled",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

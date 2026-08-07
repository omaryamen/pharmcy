"""Branch serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.branches.models import Branch
from apps.branches.serializers.settings import BranchSettingsSerializer
from apps.branches.validators import validate_branch_code, validate_coordinates


class BranchSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            "id",
            "tenant",
            "company",
            "company_name",
            "code",
            "name",
            "display_name",
            "slug",
            "branch_type",
            "status",
            "description",
            "phone",
            "mobile",
            "email",
            "website",
            "country",
            "city",
            "state",
            "district",
            "postal_code",
            "full_address",
            "latitude",
            "longitude",
            "google_maps_link",
            "timezone",
            "working_days",
            "working_hours",
            "manager",
            "manager_name",
            "logo",
            "notes",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "is_deleted", "created_at", "updated_at"]

    def get_manager_name(self, obj) -> str | None:
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.email
        return None

    def validate_code(self, value: str) -> str:
        return validate_branch_code(value)

    def validate(self, attrs):
        lat = attrs.get("latitude")
        lng = attrs.get("longitude")
        validate_coordinates(lat, lng)
        return attrs


class BranchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "company",
            "name",
            "display_name",
            "code",
            "slug",
            "branch_type",
            "description",
            "phone",
            "mobile",
            "email",
            "website",
            "country",
            "city",
            "state",
            "district",
            "postal_code",
            "full_address",
            "latitude",
            "longitude",
            "google_maps_link",
            "timezone",
            "working_days",
            "working_hours",
            "manager",
            "notes",
        ]


class BranchDetailSerializer(BranchSerializer):
    settings = BranchSettingsSerializer(read_only=True)

    class Meta(BranchSerializer.Meta):
        fields = BranchSerializer.Meta.fields + ["settings"]


class BranchAssignManagerSerializer(serializers.Serializer):
    manager_id = serializers.UUIDField()


class BranchChangeCompanySerializer(serializers.Serializer):
    new_company_id = serializers.UUIDField()

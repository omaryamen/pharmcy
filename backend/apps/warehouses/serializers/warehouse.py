"""Serializers for Enterprise Warehouse Entity and lifecycle operations."""

from __future__ import annotations

from rest_framework import serializers

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import User
from apps.warehouses.models import Warehouse
from apps.warehouses.serializers.location import StorageLocationSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "tenant",
            "company",
            "branch",
            "code",
            "name",
            "arabic_name",
            "english_name",
            "display_name",
            "description",
            "warehouse_type",
            "status",
            "manager",
            "manager_name",
            "phone",
            "email",
            "address",
            "country",
            "city",
            "district",
            "postal_code",
            "latitude",
            "longitude",
            "working_hours",
            "is_default_receiving",
            "is_default_returns",
            "is_default_quarantine",
            "is_default_damaged",
            "is_default_cold",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "display_name", "manager_name", "created_at", "updated_at"]


class WarehouseDetailSerializer(WarehouseSerializer):
    locations_count = serializers.IntegerField(source="locations.count", read_only=True)

    class Meta(WarehouseSerializer.Meta):
        fields = WarehouseSerializer.Meta.fields + ["locations_count"]


class WarehouseCreateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Warehouse
        fields = [
            "company",
            "branch",
            "code",
            "name",
            "arabic_name",
            "english_name",
            "description",
            "warehouse_type",
            "manager",
            "phone",
            "email",
            "address",
            "country",
            "city",
            "district",
            "postal_code",
            "latitude",
            "longitude",
            "working_hours",
            "is_default_receiving",
            "is_default_returns",
            "is_default_quarantine",
            "is_default_damaged",
            "is_default_cold",
            "notes",
        ]


class WarehouseUpdateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Warehouse
        fields = [
            "company",
            "branch",
            "name",
            "arabic_name",
            "english_name",
            "description",
            "warehouse_type",
            "manager",
            "phone",
            "email",
            "address",
            "country",
            "city",
            "district",
            "postal_code",
            "latitude",
            "longitude",
            "working_hours",
            "is_default_receiving",
            "is_default_returns",
            "is_default_quarantine",
            "is_default_damaged",
            "is_default_cold",
            "notes",
        ]


class ManagerAssignmentSerializer(serializers.Serializer):
    manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

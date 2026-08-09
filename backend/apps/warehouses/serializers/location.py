"""Serializers for Storage Location entities and hierarchy operations."""

from __future__ import annotations

from rest_framework import serializers

from apps.warehouses.models import StorageLocation, Warehouse


class StorageLocationSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    full_path = serializers.CharField(source="get_full_path", read_only=True)

    class Meta:
        model = StorageLocation
        fields = [
            "id",
            "tenant",
            "warehouse",
            "parent",
            "code",
            "name",
            "arabic_name",
            "english_name",
            "display_name",
            "full_path",
            "description",
            "location_type",
            "status",
            "display_order",
            "capacity",
            "capacity_unit",
            "current_utilization",
            "min_temperature",
            "max_temperature",
            "min_humidity",
            "max_humidity",
            "storage_conditions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "display_name", "full_path", "created_at", "updated_at"]


class StorageLocationDetailSerializer(StorageLocationSerializer):
    children_count = serializers.IntegerField(source="children.count", read_only=True)

    class Meta(StorageLocationSerializer.Meta):
        fields = StorageLocationSerializer.Meta.fields + ["children_count"]


class StorageLocationCreateSerializer(serializers.ModelSerializer):
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    parent = serializers.PrimaryKeyRelatedField(queryset=StorageLocation.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StorageLocation
        fields = [
            "warehouse",
            "parent",
            "code",
            "name",
            "arabic_name",
            "english_name",
            "description",
            "location_type",
            "status",
            "display_order",
            "capacity",
            "capacity_unit",
            "min_temperature",
            "max_temperature",
            "min_humidity",
            "max_humidity",
            "storage_conditions",
        ]


class StorageLocationMoveSerializer(serializers.Serializer):
    new_parent = serializers.PrimaryKeyRelatedField(queryset=StorageLocation.objects.all(), required=False, allow_null=True)

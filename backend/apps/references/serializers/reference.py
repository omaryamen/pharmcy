"""Reference serializers for Pharmaceutical Reference Data Engine."""

from __future__ import annotations

from rest_framework import serializers

from apps.references.models import (
    AtcClassification,
    DosageForm,
    Manufacturer,
    MedicineCategory,
    PackageType,
    RouteOfAdministration,
    StorageCondition,
    StrengthUnit,
    TaxCategory,
    UnitOfMeasure,
)


class MedicineCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name_en", read_only=True)

    class Meta:
        model = MedicineCategory
        fields = [
            "id",
            "code",
            "name_en",
            "name_ar",
            "slug",
            "parent",
            "parent_name",
            "icon",
            "display_order",
            "is_active",
            "is_system",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = [
            "id",
            "code",
            "legal_name",
            "display_name",
            "country_of_origin",
            "address",
            "website",
            "contact_email",
            "contact_phone",
            "registration_number",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DosageFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DosageForm
        fields = ["id", "code", "name_en", "name_ar", "description", "display_order", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class StrengthUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrengthUnit
        fields = ["id", "code", "name_en", "name_ar", "symbol", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ["id", "code", "name_en", "name_ar", "symbol", "unit_type", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageType
        fields = ["id", "code", "name_en", "name_ar", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RouteOfAdministrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteOfAdministration
        fields = ["id", "code", "name_en", "name_ar", "abbreviation", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AtcClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtcClassification
        fields = ["id", "code", "level", "name_en", "name_ar", "parent", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class StorageConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageCondition
        fields = [
            "id",
            "code",
            "name_en",
            "name_ar",
            "min_temperature",
            "max_temperature",
            "requires_refrigeration",
            "protect_from_light",
            "humidity_controlled",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaxCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxCategory
        fields = ["id", "code", "name_en", "name_ar", "tax_rate", "is_exempt", "is_active", "is_system", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

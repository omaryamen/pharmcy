"""Django Admin configuration for Pharmaceutical Reference Data Engine."""

from __future__ import annotations

from django.contrib import admin

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


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "parent", "display_order", "is_active"]
    search_fields = ["name_en", "name_ar", "code"]


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ["display_name", "legal_name", "code", "country_of_origin", "is_active"]
    search_fields = ["display_name", "legal_name", "code"]


@admin.register(DosageForm)
class DosageFormAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "is_system", "is_active"]


@admin.register(StrengthUnit)
class StrengthUnitAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name_en", "code", "is_system"]


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code", "unit_type"]


@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ["name_en", "name_ar", "code"]


@admin.register(RouteOfAdministration)
class RouteOfAdministrationAdmin(admin.ModelAdmin):
    list_display = ["name_en", "code", "abbreviation"]


@admin.register(AtcClassification)
class AtcClassificationAdmin(admin.ModelAdmin):
    list_display = ["code", "name_en", "level", "parent"]
    search_fields = ["code", "name_en"]


@admin.register(StorageCondition)
class StorageConditionAdmin(admin.ModelAdmin):
    list_display = ["name_en", "code", "requires_refrigeration", "protect_from_light"]


@admin.register(TaxCategory)
class TaxCategoryAdmin(admin.ModelAdmin):
    list_display = ["name_en", "code", "tax_rate", "is_exempt"]

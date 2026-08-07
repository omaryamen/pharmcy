"""Reference selector functions for tenant-scoped reference data queries."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

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


class ReferenceSelector:
    def list_categories(self, tenant, *, search: str | None = None) -> QuerySet[MedicineCategory]:
        qs = MedicineCategory.objects.filter(tenant=tenant, is_deleted=False).select_related("parent")
        if search:
            qs = qs.filter(name_en__icontains=search) | qs.filter(name_ar__icontains=search) | qs.filter(code__icontains=search)
        return qs

    def get_category_tree(self, tenant) -> list[dict]:
        roots = MedicineCategory.objects.filter(tenant=tenant, parent__isnull=True, is_deleted=False).prefetch_related("children")

        def build_node(cat):
            return {
                "id": str(cat.id),
                "code": cat.code,
                "name_en": cat.name_en,
                "name_ar": cat.name_ar,
                "children": [build_node(child) for child in cat.children.filter(is_deleted=False)],
            }

        return [build_node(r) for r in roots]

    def list_manufacturers(self, tenant, *, search: str | None = None) -> QuerySet[Manufacturer]:
        qs = Manufacturer.objects.filter(tenant=tenant, is_deleted=False)
        if search:
            qs = qs.filter(display_name__icontains=search) | qs.filter(legal_name__icontains=search) | qs.filter(code__icontains=search)
        return qs

    def list_dosage_forms(self, tenant) -> QuerySet[DosageForm]:
        return DosageForm.objects.filter(tenant=tenant, is_deleted=False)

    def list_strength_units(self, tenant) -> QuerySet[StrengthUnit]:
        return StrengthUnit.objects.filter(tenant=tenant, is_deleted=False)

    def list_units_of_measure(self, tenant) -> QuerySet[UnitOfMeasure]:
        return UnitOfMeasure.objects.filter(tenant=tenant, is_deleted=False)

    def list_package_types(self, tenant) -> QuerySet[PackageType]:
        return PackageType.objects.filter(tenant=tenant, is_deleted=False)

    def list_routes(self, tenant) -> QuerySet[RouteOfAdministration]:
        return RouteOfAdministration.objects.filter(tenant=tenant, is_deleted=False)

    def list_atc_classifications(self, tenant, level: int | None = None) -> QuerySet[AtcClassification]:
        qs = AtcClassification.objects.filter(tenant=tenant, is_deleted=False)
        if level:
            qs = qs.filter(level=level)
        return qs

    def list_storage_conditions(self, tenant) -> QuerySet[StorageCondition]:
        return StorageCondition.objects.filter(tenant=tenant, is_deleted=False)

    def list_tax_categories(self, tenant) -> QuerySet[TaxCategory]:
        return TaxCategory.objects.filter(tenant=tenant, is_deleted=False)

    def get_reference_stats(self, tenant) -> dict[str, Any]:
        return {
            "tenant_id": str(tenant.pk),
            "categories_count": MedicineCategory.objects.filter(tenant=tenant, is_deleted=False).count(),
            "manufacturers_count": Manufacturer.objects.filter(tenant=tenant, is_deleted=False).count(),
            "dosage_forms_count": DosageForm.objects.filter(tenant=tenant, is_deleted=False).count(),
            "strength_units_count": StrengthUnit.objects.filter(tenant=tenant, is_deleted=False).count(),
            "uom_count": UnitOfMeasure.objects.filter(tenant=tenant, is_deleted=False).count(),
            "routes_count": RouteOfAdministration.objects.filter(tenant=tenant, is_deleted=False).count(),
            "tax_categories_count": TaxCategory.objects.filter(tenant=tenant, is_deleted=False).count(),
        }

"""Reference API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.references.api.views import (
    AtcClassificationViewSet,
    DosageFormViewSet,
    ManufacturerViewSet,
    MedicineCategoryViewSet,
    PackageTypeViewSet,
    ReferenceSeedView,
    ReferenceStatsView,
    RouteOfAdministrationViewSet,
    StorageConditionViewSet,
    StrengthUnitViewSet,
    TaxCategoryViewSet,
    UnitOfMeasureViewSet,
)

router = DefaultRouter()
router.register(r"categories", MedicineCategoryViewSet, basename="reference-category")
router.register(r"manufacturers", ManufacturerViewSet, basename="reference-manufacturer")
router.register(r"dosage-forms", DosageFormViewSet, basename="reference-dosage-form")
router.register(r"strength-units", StrengthUnitViewSet, basename="reference-strength-unit")
router.register(r"units-of-measure", UnitOfMeasureViewSet, basename="reference-uom")
router.register(r"package-types", PackageTypeViewSet, basename="reference-package-type")
router.register(r"routes", RouteOfAdministrationViewSet, basename="reference-route")
router.register(r"atc", AtcClassificationViewSet, basename="reference-atc")
router.register(r"storage-conditions", StorageConditionViewSet, basename="reference-storage-condition")
router.register(r"tax-categories", TaxCategoryViewSet, basename="reference-tax-category")

urlpatterns = [
    path("seed/", ReferenceSeedView.as_view(), name="reference-seed"),
    path("stats/", ReferenceStatsView.as_view(), name="reference-stats"),
    path("", include(router.urls)),
]

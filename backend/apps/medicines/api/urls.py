"""Medicine API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.medicines.api.views import MedicineStatsView, MedicineViewSet

router = DefaultRouter()
router.register(r"", MedicineViewSet, basename="medicine-master")

urlpatterns = [
    path("stats/", MedicineStatsView.as_view(), name="medicine-stats"),
    path("", include(router.urls)),
]

"""URL Configuration for Enterprise Supplier Management APIs."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.suppliers.api.views import SupplierStatsView, SupplierViewSet

router = DefaultRouter()
router.register(r"", SupplierViewSet, basename="supplier")

urlpatterns = [
    path("stats/", SupplierStatsView.as_view(), name="supplier-stats"),
    path("", include(router.urls)),
]

"""Company API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.companies.api.views import CompanySettingsViewSet, CompanyStatsView, CompanyViewSet

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="company")

urlpatterns = [
    path("<uuid:company_id>/settings/", CompanySettingsViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="company-settings"),
    path("<uuid:company_id>/stats/", CompanyStatsView.as_view(), name="company-stats"),
    path("", include(router.urls)),
]

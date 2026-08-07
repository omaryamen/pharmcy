"""Branch API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.branches.api.views import BranchSettingsViewSet, BranchStatsView, BranchViewSet

router = DefaultRouter()
router.register(r"", BranchViewSet, basename="branch")

urlpatterns = [
    path("<uuid:branch_id>/settings/", BranchSettingsViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="branch-settings"),
    path("<uuid:branch_id>/stats/", BranchStatsView.as_view(), name="branch-stats"),
    path("", include(router.urls)),
]

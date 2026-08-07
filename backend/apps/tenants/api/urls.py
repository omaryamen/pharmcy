"""Tenant API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.api.views import (
    TenantDomainViewSet,
    TenantLimitsView,
    TenantProfileViewSet,
    TenantSettingsViewSet,
    TenantStatsView,
    TenantSubscriptionViewSet,
    TenantViewSet,
)

router = DefaultRouter()
router.register(r"", TenantViewSet, basename="tenant")

urlpatterns = [
    path("me/profile/", TenantProfileViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="tenant-profile"),
    path("me/settings/", TenantSettingsViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="tenant-settings"),
    path("me/subscription/", TenantSubscriptionViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="tenant-subscription"),
    path("me/domains/", TenantDomainViewSet.as_view({"get": "list", "post": "create"}), name="tenant-domains-list"),
    path("me/domains/<uuid:pk>/", TenantDomainViewSet.as_view({"delete": "destroy"}), name="tenant-domains-detail"),
    path("me/domains/<uuid:pk>/verify/", TenantDomainViewSet.as_view({"post": "verify"}), name="tenant-domains-verify"),
    path("me/domains/<uuid:pk>/set-primary/", TenantDomainViewSet.as_view({"post": "set_primary"}), name="tenant-domains-set-primary"),
    path("me/stats/", TenantStatsView.as_view(), name="tenant-stats"),
    path("me/limits/", TenantLimitsView.as_view(), name="tenant-limits"),
    path("", include(router.urls)),
]
